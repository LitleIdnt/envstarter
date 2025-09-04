"""
Environment launching functionality for EnvStarter.
"""

import os
import subprocess
import webbrowser
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from envstarter.core.models import Environment, Application, Website


class LaunchWorker(QThread):
    """Worker thread for launching environment items."""
    
    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    item_launched = pyqtSignal(str, bool)    # item name, success
    launch_completed = pyqtSignal(bool)      # overall success
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self, environment: Environment):
        super().__init__()
        self.environment = environment
        self.launched_processes = []
    
    def run(self):
        """Run the launch process."""
        try:
            total_items = self.environment.get_total_items()
            if total_items == 0:
                self.launch_completed.emit(False)
                return
            
            current_item = 0
            success_count = 0
            
            # Apply startup delay if specified
            if self.environment.startup_delay > 0:
                self.progress_updated.emit(0, f"Waiting {self.environment.startup_delay} seconds...")
                time.sleep(self.environment.startup_delay)
            
            # Launch applications
            for app in self.environment.applications:
                current_item += 1
                progress = int((current_item / total_items) * 100)
                
                self.progress_updated.emit(progress, f"Starting {app.name}...")
                
                try:
                    success = self._launch_application(app)
                    if success:
                        success_count += 1
                    self.item_launched.emit(app.name, success)
                except Exception as e:
                    self.error_occurred.emit(f"Error launching {app.name}: {str(e)}")
                    self.item_launched.emit(app.name, False)
                
                # Small delay between launches
                time.sleep(0.5)
            
            # Launch websites
            for website in self.environment.websites:
                current_item += 1
                progress = int((current_item / total_items) * 100)
                
                self.progress_updated.emit(progress, f"Opening {website.name}...")
                
                try:
                    success = self._launch_website(website)
                    if success:
                        success_count += 1
                    self.item_launched.emit(website.name, success)
                except Exception as e:
                    self.error_occurred.emit(f"Error opening {website.name}: {str(e)}")
                    self.item_launched.emit(website.name, False)
                
                # Small delay between launches
                time.sleep(0.5)
            
            # Completed
            self.progress_updated.emit(100, "Launch completed!")
            overall_success = success_count > 0
            self.launch_completed.emit(overall_success)
            
        except Exception as e:
            self.error_occurred.emit(f"Launch process failed: {str(e)}")
            self.launch_completed.emit(False)
    
    def _launch_application(self, app: Application) -> bool:
        """Launch a single application."""
        try:
            # Expand environment variables in path
            app_path = os.path.expandvars(app.path)
            
            # Handle different types of executables
            if not Path(app_path).exists():
                # Try to find in PATH
                if os.name == 'nt':  # Windows
                    # Check common locations and PATH
                    possible_paths = [
                        app_path,
                        f"{app_path}.exe",
                        os.path.join("C:\\Program Files", app.name, f"{app.name}.exe"),
                        os.path.join("C:\\Program Files (x86)", app.name, f"{app.name}.exe"),
                    ]
                    
                    found_path = None
                    for path in possible_paths:
                        if Path(path).exists():
                            found_path = path
                            break
                    
                    if not found_path:
                        # Try using where command to find in PATH
                        try:
                            result = subprocess.run(['where', app_path], 
                                                  capture_output=True, text=True, shell=True)
                            if result.returncode == 0:
                                found_path = result.stdout.strip().split('\n')[0]
                        except:
                            pass
                    
                    if not found_path:
                        return False
                    
                    app_path = found_path
            
            # Prepare command
            cmd = [app_path]
            if app.arguments:
                # Simple argument splitting (could be enhanced)
                args = app.arguments.split()
                cmd.extend(args)
            
            # Set working directory
            cwd = None
            if app.working_directory and Path(app.working_directory).exists():
                cwd = app.working_directory
            
            # Launch process
            if os.name == 'nt':  # Windows
                # Use CREATE_NO_WINDOW to avoid showing command prompt
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                process = subprocess.Popen(cmd, cwd=cwd)
            
            if not app.wait_for_exit:
                # Store process for potential cleanup
                self.launched_processes.append(process)
            else:
                # Wait for process to complete
                process.wait()
            
            return True
            
        except Exception as e:
            print(f"Error launching application {app.name}: {e}")
            return False
    
    def _launch_website(self, website: Website) -> bool:
        """Launch a website."""
        try:
            if website.browser and Path(website.browser).exists():
                # Use specific browser
                if os.name == 'nt':
                    subprocess.Popen([website.browser, website.url],
                                   creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
                else:
                    subprocess.Popen([website.browser, website.url])
            else:
                # Use system default browser
                webbrowser.open(website.url, new=2 if website.new_tab else 1)
            
            return True
            
        except Exception as e:
            print(f"Error opening website {website.name}: {e}")
            return False
    
    def stop_launched_processes(self):
        """Terminate all launched processes."""
        for process in self.launched_processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    # Give process time to terminate gracefully
                    time.sleep(1)
                    if process.poll() is None:
                        process.kill()
            except:
                pass
        self.launched_processes.clear()


class EnvironmentLauncher(QObject):
    """Main launcher for environments."""
    
    launch_started = pyqtSignal(str)         # environment name
    progress_updated = pyqtSignal(int, str)  # progress, message
    item_launched = pyqtSignal(str, bool)    # item name, success
    launch_completed = pyqtSignal(str, bool) # environment name, success
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self):
        super().__init__()
        self.current_worker = None
        self.current_environment = None
    
    def launch_environment(self, environment: Environment):
        """Launch an environment."""
        if self.current_worker and self.current_worker.isRunning():
            self.error_occurred.emit("Another environment is currently being launched")
            return
        
        self.current_environment = environment
        self.launch_started.emit(environment.name)
        
        # Create and start worker thread
        self.current_worker = LaunchWorker(environment)
        self.current_worker.progress_updated.connect(self.progress_updated)
        self.current_worker.item_launched.connect(self.item_launched)
        self.current_worker.launch_completed.connect(self._on_launch_completed)
        self.current_worker.error_occurred.connect(self.error_occurred)
        
        self.current_worker.start()
    
    def _on_launch_completed(self, success: bool):
        """Handle launch completion."""
        if self.current_environment:
            self.launch_completed.emit(self.current_environment.name, success)
    
    def stop_current_environment(self):
        """Stop the currently launching environment."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop_launched_processes()
            self.current_worker.terminate()
            self.current_worker.wait(3000)  # Wait up to 3 seconds
    
    def is_launching(self) -> bool:
        """Check if currently launching an environment."""
        return self.current_worker and self.current_worker.isRunning()