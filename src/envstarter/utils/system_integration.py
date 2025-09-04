"""
Windows system integration utilities.
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Optional, List, Dict
import subprocess


class SystemIntegration:
    """Handles Windows system integration features."""
    
    def __init__(self):
        self.app_name = "EnvStarter"
        self.executable_path = self._get_executable_path()
    
    def _get_executable_path(self) -> str:
        """Get the path to the current executable."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as Python script
            return sys.executable + " " + os.path.abspath(sys.argv[0])
    
    def is_tray_available(self) -> bool:
        """Check if system tray is available."""
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon
            return QSystemTrayIcon.isSystemTrayAvailable()
        except:
            return False
    
    def add_to_startup(self) -> bool:
        """Add EnvStarter to Windows startup."""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.executable_path)
            return True
        except Exception as e:
            print(f"Error adding to startup: {e}")
            return False
    
    def remove_from_startup(self) -> bool:
        """Remove EnvStarter from Windows startup."""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, self.app_name)
            return True
        except FileNotFoundError:
            # Key doesn't exist, already removed
            return True
        except Exception as e:
            print(f"Error removing from startup: {e}")
            return False
    
    def is_in_startup(self) -> bool:
        """Check if EnvStarter is in Windows startup."""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return False
    
    def create_desktop_shortcut(self) -> bool:
        """Create a desktop shortcut for EnvStarter."""
        try:
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                # Try public desktop
                desktop = Path("C:\\Users\\Public\\Desktop")
            
            shortcut_path = desktop / f"{self.app_name}.lnk"
            
            # Create shortcut using PowerShell
            ps_command = f'''
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{self.executable_path.split()[0]}"
            $Shortcut.Arguments = "{' '.join(self.executable_path.split()[1:])}"
            $Shortcut.Description = "Start your perfect work environment with one click"
            $Shortcut.Save()
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating desktop shortcut: {e}")
            return False
    
    def remove_desktop_shortcut(self) -> bool:
        """Remove desktop shortcut."""
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / f"{self.app_name}.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                return True
            
            # Try public desktop
            desktop = Path("C:\\Users\\Public\\Desktop")
            shortcut_path = desktop / f"{self.app_name}.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                return True
            
            return True  # Shortcut doesn't exist, consider it removed
            
        except Exception as e:
            print(f"Error removing desktop shortcut: {e}")
            return False
    
    def get_installed_programs(self) -> List[Dict[str, str]]:
        """Get list of installed programs from Windows registry."""
        programs = []
        
        # Registry paths to check
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hive, path in registry_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    install_location = ""
                                    executable_path = ""
                                    
                                    # Try to get install location
                                    try:
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    except FileNotFoundError:
                                        pass
                                    
                                    # Try to get executable path
                                    try:
                                        executable_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                        # Clean up executable path (remove arguments and quotes)
                                        if executable_path:
                                            executable_path = executable_path.split(',')[0].strip('"')
                                    except FileNotFoundError:
                                        pass
                                    
                                    # If no executable found but we have install location, try to guess
                                    if not executable_path and install_location:
                                        possible_exe = Path(install_location) / f"{display_name}.exe"
                                        if possible_exe.exists():
                                            executable_path = str(possible_exe)
                                    
                                    if display_name and (executable_path or install_location):
                                        programs.append({
                                            "name": display_name,
                                            "path": executable_path or install_location,
                                            "install_location": install_location
                                        })
                                
                                except FileNotFoundError:
                                    # No DisplayName, skip
                                    continue
                        except Exception:
                            # Skip problematic entries
                            continue
            except Exception as e:
                print(f"Error accessing registry {path}: {e}")
                continue
        
        # Remove duplicates and sort
        unique_programs = {}
        for program in programs:
            key = program["name"].lower()
            if key not in unique_programs:
                unique_programs[key] = program
        
        return sorted(unique_programs.values(), key=lambda x: x["name"].lower())
    
    def find_common_applications(self) -> List[Dict[str, str]]:
        """Find common applications in standard locations."""
        common_apps = []
        
        # Common application locations
        common_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming")
        ]
        
        # Common application names to look for
        common_names = [
            "Chrome", "Firefox", "Edge", "Notepad++", "VSCode", "Code",
            "Discord", "Slack", "Teams", "Zoom", "Steam", "Spotify",
            "Photoshop", "Illustrator", "Git", "Python", "Node"
        ]
        
        for base_path in common_paths:
            try:
                if not Path(base_path).exists():
                    continue
                    
                for item in Path(base_path).iterdir():
                    if item.is_dir():
                        folder_name = item.name.lower()
                        
                        # Check if folder name contains any common app name
                        for app_name in common_names:
                            if app_name.lower() in folder_name:
                                # Look for executable files
                                for exe_file in item.rglob("*.exe"):
                                    if exe_file.is_file():
                                        common_apps.append({
                                            "name": exe_file.stem,
                                            "path": str(exe_file),
                                            "install_location": str(item)
                                        })
                                        break  # Only add first exe found
                                break
            except PermissionError:
                # Skip directories we can't access
                continue
            except Exception as e:
                print(f"Error scanning {base_path}: {e}")
                continue
        
        return common_apps