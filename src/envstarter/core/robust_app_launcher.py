"""
🚀 ROBUST APPLICATION LAUNCHER 🚀
Finds and launches applications even when paths are wrong!
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import winreg
import psutil


class RobustApplicationLauncher:
    """
    ROBUST APPLICATION LAUNCHER
    Finds applications even when paths are incorrect or missing!
    """
    
    def __init__(self):
        self.common_app_paths = self._get_common_app_paths()
        self.registry_apps = self._get_registry_apps()
        
    def _get_common_app_paths(self) -> List[str]:
        """Get common application search paths."""
        paths = []
        
        if os.name == 'nt':  # Windows
            paths.extend([
                os.path.expandvars(r"C:\Program Files"),
                os.path.expandvars(r"C:\Program Files (x86)"),
                os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
                os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
                os.path.expandvars(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"),
                os.path.expandvars(r"C:\Windows\System32"),
                os.path.expandvars(r"C:\Windows"),
            ])
        else:  # Linux/Mac
            paths.extend([
                "/usr/bin",
                "/usr/local/bin", 
                "/opt",
                "/Applications",  # macOS
                "/usr/share/applications",  # Linux
                os.path.expanduser("~/Applications"),
                os.path.expanduser("~/.local/bin"),
            ])
            
        return paths
        
    def _get_registry_apps(self) -> Dict[str, str]:
        """Get installed applications from Windows registry."""
        apps = {}
        
        if os.name != 'nt':
            return apps
            
        try:
            import winreg
            
            # Check multiple registry locations
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            
            for hkey, path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        
                                        if install_location and os.path.exists(install_location):
                                            apps[display_name.lower()] = install_location
                                            
                                    except FileNotFoundError:
                                        continue
                            except:
                                continue
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Registry search error: {e}")
            
        return apps
        
    def find_application(self, app_name: str, app_path: str) -> Optional[str]:
        """Find the actual path to an application."""
        
        # Method 1: Try the provided path first
        if app_path and os.path.exists(app_path):
            return app_path
            
        # Method 2: Try path expansion
        expanded_path = os.path.expandvars(app_path) if app_path else ""
        if expanded_path and os.path.exists(expanded_path):
            return expanded_path
            
        # Method 3: Check if it's in PATH
        which_result = shutil.which(app_name) or shutil.which(app_path)
        if which_result:
            return which_result
            
        # Method 4: Search common application directories
        exe_name = Path(app_path).name if app_path else f"{app_name}.exe"
        
        for search_path in self.common_app_paths:
            if os.path.exists(search_path):
                # Search recursively (but limit depth to avoid slowness)
                found = self._search_directory(search_path, exe_name, max_depth=3)
                if found:
                    return found
                    
        # Method 5: Search registry installations
        app_name_lower = app_name.lower()
        for reg_name, install_path in self.registry_apps.items():
            if app_name_lower in reg_name or reg_name in app_name_lower:
                # Look for executables in this install path
                if os.path.exists(install_path):
                    found = self._search_directory(install_path, exe_name, max_depth=2)
                    if found:
                        return found
                        
        # Method 6: Try common executable variations
        if os.name == 'nt':
            variations = [
                f"{app_name}.exe",
                f"{app_name}.cmd",
                f"{app_name}.bat",
                app_name
            ]
        else:
            variations = [app_name, f"{app_name}.app"]  # macOS .app bundles
            
        for variation in variations:
            which_result = shutil.which(variation)
            if which_result:
                return which_result
                
        # Method 7: Last resort - search specific known applications
        return self._find_known_application(app_name, app_path)
        
    def _search_directory(self, directory: str, filename: str, max_depth: int = 2) -> Optional[str]:
        """Search for a file in directory with limited depth."""
        try:
            for root, dirs, files in os.walk(directory):
                # Limit search depth
                depth = root.replace(directory, '').count(os.sep)
                if depth >= max_depth:
                    dirs[:] = []  # Don't search deeper
                    
                for file in files:
                    if file.lower() == filename.lower():
                        full_path = os.path.join(root, file)
                        if os.access(full_path, os.X_OK):  # Check if executable
                            return full_path
                            
        except (PermissionError, OSError):
            pass
            
        return None
        
    def _find_known_application(self, app_name: str, app_path: str) -> Optional[str]:
        """Find common applications by name."""
        app_lower = app_name.lower()
        
        if os.name == 'nt':  # Windows
            known_apps = {
                'calculator': ['calc.exe', 'calculator.exe'],
                'notepad': ['notepad.exe'],
                'cmd': ['cmd.exe'],
                'powershell': ['powershell.exe'],
                'explorer': ['explorer.exe'],
                'chrome': [
                    r'Google\Chrome\Application\chrome.exe',
                    r'Program Files\Google\Chrome\Application\chrome.exe',
                    r'Program Files (x86)\Google\Chrome\Application\chrome.exe'
                ],
                'firefox': [
                    r'Mozilla Firefox\firefox.exe',
                    r'Program Files\Mozilla Firefox\firefox.exe',
                    r'Program Files (x86)\Mozilla Firefox\firefox.exe'
                ],
                'edge': ['msedge.exe'],
                'code': [
                    r'Microsoft VS Code\Code.exe',
                    r'Programs\Microsoft VS Code\Code.exe'
                ],
                'vmware': [
                    r'VMware\VMware Workstation\vmware.exe',
                    r'Program Files (x86)\VMware\VMware Workstation\vmware.exe'
                ],
                'virtualbox': [
                    r'Oracle\VirtualBox\VirtualBox.exe',
                    r'Program Files\Oracle\VirtualBox\VirtualBox.exe'
                ]
            }
        else:  # Linux/Mac
            known_apps = {
                'calculator': ['gnome-calculator', 'kcalc', 'Calculator.app'],
                'firefox': ['firefox'],
                'chrome': ['google-chrome', 'chromium-browser'],
                'code': ['code'],
                'gedit': ['gedit'],
                'kate': ['kate'],
            }
            
        if app_lower in known_apps:
            for possible_path in known_apps[app_lower]:
                # Try direct path
                full_path = shutil.which(possible_path)
                if full_path:
                    return full_path
                    
                # Try in common directories
                for base_path in self.common_app_paths:
                    candidate = os.path.join(base_path, possible_path)
                    if os.path.exists(candidate):
                        return candidate
                        
        return None
        
    def launch_application(self, app_name: str, app_path: str, arguments: str = "", 
                          working_dir: str = "", environment_vars: dict = None) -> Optional[subprocess.Popen]:
        """Launch an application with robust path finding."""
        
        print(f"🚀 Launching: {app_name}")
        print(f"   Original path: {app_path}")
        
        # Find the actual application path
        actual_path = self.find_application(app_name, app_path)
        
        if not actual_path:
            print(f"❌ Could not find application: {app_name}")
            print(f"   Searched for: {app_path}")
            print(f"   Try these alternatives:")
            
            # Suggest alternatives
            suggestions = self._suggest_alternatives(app_name, app_path)
            for suggestion in suggestions:
                print(f"     - {suggestion}")
                
            return None
            
        print(f"✅ Found application at: {actual_path}")
        
        # Prepare command
        cmd = [actual_path]
        if arguments:
            cmd.extend(arguments.split())
            
        # Prepare environment
        env = os.environ.copy()
        if environment_vars:
            env.update(environment_vars)
            
        # Set working directory
        cwd = working_dir if working_dir and os.path.exists(working_dir) else None
        
        try:
            # Launch process
            if os.name == 'nt':
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(cmd, cwd=cwd, env=env)
                
            print(f"✅ Application launched successfully! PID: {process.pid}")
            return process
            
        except Exception as e:
            print(f"❌ Failed to launch application: {e}")
            return None
            
    def _suggest_alternatives(self, app_name: str, app_path: str) -> List[str]:
        """Suggest alternative paths for the application."""
        suggestions = []
        
        # Check PATH
        which_result = shutil.which(app_name)
        if which_result:
            suggestions.append(f"Found in PATH: {which_result}")
            
        # Check common variations
        if os.name == 'nt':
            variations = [f"{app_name}.exe", f"{app_name}.cmd", f"{app_name}.bat"]
        else:
            variations = [app_name]
            
        for var in variations:
            which_var = shutil.which(var)
            if which_var and which_var not in suggestions:
                suggestions.append(f"Alternative: {which_var}")
                
        return suggestions[:5]  # Limit suggestions


# Global launcher instance
_launcher = None

def get_robust_launcher() -> RobustApplicationLauncher:
    """Get the global robust launcher instance."""
    global _launcher
    if _launcher is None:
        _launcher = RobustApplicationLauncher()
    return _launcher


def launch_application_robust(app_name: str, app_path: str, arguments: str = "", 
                            working_dir: str = "", environment_vars: dict = None) -> Optional[subprocess.Popen]:
    """Quick function to launch an application robustly."""
    launcher = get_robust_launcher()
    return launcher.launch_application(app_name, app_path, arguments, working_dir, environment_vars)


if __name__ == "__main__":
    # Test the launcher
    launcher = RobustApplicationLauncher()
    
    # Test finding calculator
    calc_path = launcher.find_application("Calculator", "calc.exe")
    print(f"Calculator found at: {calc_path}")
    
    # Test launching calculator
    if calc_path:
        process = launcher.launch_application("Calculator", "calc.exe")
        if process:
            print(f"Calculator launched with PID: {process.pid}")
        else:
            print("Failed to launch calculator")
    else:
        print("Calculator not found")