"""
Windows system integration utilities.
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Optional, List, Dict
import subprocess
import json
import time


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
        """Get list of installed programs from Windows registry - FAST version."""
        programs = []
        
        # Only scan essential registry paths for speed
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hive, path in registry_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    
                    # Limit to first 200 entries for speed
                    for i in range(min(num_subkeys, 200)):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    
                                    # Skip system updates and patches for speed
                                    if any(skip in display_name.lower() for skip in ['update', 'patch', 'hotfix', 'kb']):
                                        continue
                                    
                                    executable_path = ""
                                    
                                    # Only check for executable path, skip install location for speed
                                    try:
                                        executable_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                        if executable_path:
                                            executable_path = executable_path.split(',')[0].strip('"')
                                    except FileNotFoundError:
                                        # Try InstallLocation as fallback
                                        try:
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                            if install_location:
                                                possible_exe = Path(install_location) / f"{display_name}.exe"
                                                if possible_exe.exists():
                                                    executable_path = str(possible_exe)
                                        except:
                                            pass
                                    
                                    if display_name and executable_path:
                                        programs.append({
                                            "name": display_name,
                                            "path": executable_path,
                                            "install_location": ""
                                        })
                                
                                except FileNotFoundError:
                                    continue
                        except Exception:
                            continue
            except Exception:
                continue
        
        # Fast deduplication
        seen = set()
        unique_programs = []
        for program in programs:
            key = program["name"].lower()
            if key not in seen:
                seen.add(key)
                unique_programs.append(program)
        
        return sorted(unique_programs, key=lambda x: x["name"].lower())
    
    def find_common_applications(self) -> List[Dict[str, str]]:
        """Find common applications in standard locations - FAST version."""
        common_apps = []
        
        # Specific known app paths for speed
        known_apps = [
            ("Google Chrome", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
            ("Google Chrome", "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"),
            ("Microsoft Edge", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"),
            ("Firefox", "C:\\Program Files\\Mozilla Firefox\\firefox.exe"),
            ("Firefox", "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"),
            ("Visual Studio Code", "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
            ("Notepad++", "C:\\Program Files\\Notepad++\\notepad++.exe"),
            ("Notepad++", "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"),
            ("Discord", "C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\Update.exe"),
            ("Microsoft Teams", "C:\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe"),
            ("Slack", "C:\\Users\\%USERNAME%\\AppData\\Local\\slack\\slack.exe"),
            ("Zoom", "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"),
            ("Steam", "C:\\Program Files (x86)\\Steam\\steam.exe"),
            ("Spotify", "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe"),
        ]
        
        # Quick check for known applications
        for app_name, app_path in known_apps:
            try:
                expanded_path = os.path.expandvars(app_path)
                if Path(expanded_path).exists():
                    common_apps.append({
                        "name": app_name,
                        "path": expanded_path,
                        "install_location": str(Path(expanded_path).parent)
                    })
            except Exception:
                continue
        
        return common_apps
    
    def get_windows_store_apps(self) -> List[Dict[str, str]]:
        """Get Windows Store/UWP applications using PowerShell - FAST version."""
        store_apps = []
        
        try:
            # Simplified PowerShell command for speed - no manifest parsing
            ps_command = '''
            Get-AppxPackage | Where-Object { 
                $_.SignatureKind -eq "Store" -and 
                $_.Name -notlike "*Microsoft.Windows*" -and 
                $_.Name -notlike "*Microsoft.Xbox*" -and
                $_.Name -like "*.*" 
            } | Select-Object -First 20 Name, PackageFullName | ForEach-Object { 
                Write-Output "$($_.Name)|$($_.PackageFullName)" 
            }
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,  # Reduced timeout for speed
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('|')
                        if len(parts) >= 2:
                            display_name = parts[0].strip()
                            package_name = parts[1].strip()
                            
                            if display_name and package_name:
                                # Create launch command for Store app
                                launch_path = f"shell:appsFolder\\{package_name}!App"
                                
                                store_apps.append({
                                    "name": display_name,
                                    "path": launch_path,
                                    "install_location": "",
                                    "type": "store_app"
                                })
        
        except Exception as e:
            print(f"Error getting Windows Store apps: {e}")
        
        return store_apps
    
    def get_office_apps(self) -> List[Dict[str, str]]:
        """Get Microsoft Office applications."""
        office_apps = []
        
        # Common Office installation paths
        office_paths = [
            r"C:\Program Files\Microsoft Office\root\Office16",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16", 
            r"C:\Program Files\Microsoft Office\Office16",
            r"C:\Program Files (x86)\Microsoft Office\Office16",
            r"C:\Program Files\Microsoft Office\Office15",
            r"C:\Program Files (x86)\Microsoft Office\Office15",
        ]
        
        # Office executables to look for
        office_exes = {
            "WINWORD.EXE": "Microsoft Word",
            "EXCEL.EXE": "Microsoft Excel", 
            "POWERPNT.EXE": "Microsoft PowerPoint",
            "OUTLOOK.EXE": "Microsoft Outlook",
            "ONENOTE.EXE": "Microsoft OneNote",
            "MSACCESS.EXE": "Microsoft Access",
            "msteams.exe": "Microsoft Teams",
        }
        
        for office_path in office_paths:
            if os.path.exists(office_path):
                for exe_name, app_name in office_exes.items():
                    exe_path = os.path.join(office_path, exe_name)
                    if os.path.exists(exe_path):
                        office_apps.append({
                            "name": app_name,
                            "path": exe_path,
                            "install_location": office_path
                        })
        
        return office_apps
    
    def get_modern_apps(self) -> List[Dict[str, str]]:
        """Get modern applications from specific known locations - FAST version."""
        modern_apps = []
        
        # Specific known modern app executables
        known_modern_apps = [
            ("Discord", "C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\app-*\\Discord.exe"),
            ("Slack", "C:\\Users\\%USERNAME%\\AppData\\Local\\slack\\slack.exe"), 
            ("Spotify", "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe"),
            ("WhatsApp", "C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe"),
            ("Zoom", "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"),
        ]
        
        # Quick check for specific known apps only
        for app_name, app_path_pattern in known_modern_apps:
            try:
                expanded_path = os.path.expandvars(app_path_pattern)
                
                # Handle wildcards for Discord (multiple versions)
                if '*' in expanded_path:
                    import glob
                    matches = glob.glob(expanded_path)
                    if matches:
                        expanded_path = matches[0]  # Use first match
                
                if Path(expanded_path).exists():
                    modern_apps.append({
                        "name": app_name,
                        "path": expanded_path,
                        "install_location": str(Path(expanded_path).parent)
                    })
            except Exception:
                continue
        
        return modern_apps
    
    def _resolve_shortcut(self, lnk_path: str) -> Optional[str]:
        """Resolve a Windows shortcut (.lnk) to its target."""
        try:
            # Use PowerShell to resolve shortcut
            ps_command = f'''
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{lnk_path}")
            Write-Output $Shortcut.TargetPath
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                target = result.stdout.strip()
                if target and os.path.exists(target):
                    return target
        except:
            pass
        
        return None
    
    def get_all_applications(self, progress_callback=None) -> List[Dict[str, str]]:
        """Get comprehensive list of all applications - FAST version."""
        all_apps = []
        
        if progress_callback:
            progress_callback(10, "Scanning registry programs...")
        registry_apps = self.get_installed_programs()
        all_apps.extend(registry_apps)
        
        if progress_callback:
            progress_callback(30, "Scanning common applications...")
        common_apps = self.find_common_applications()
        all_apps.extend(common_apps)
        
        if progress_callback:
            progress_callback(50, "Scanning Office applications...")
        office_apps = self.get_office_apps()
        all_apps.extend(office_apps)
        
        if progress_callback:
            progress_callback(70, "Scanning modern applications...")
        modern_apps = self.get_modern_apps()
        all_apps.extend(modern_apps)
        
        # Store apps are slow, make them optional for now
        if progress_callback:
            progress_callback(85, "Scanning Windows Store apps (optional)...")
        try:
            store_apps = self.get_windows_store_apps()
            all_apps.extend(store_apps)
        except Exception:
            # Skip store apps if they're taking too long
            pass
        
        # Remove duplicates based on name (case insensitive)
        unique_apps = {}
        for app in all_apps:
            key = app["name"].lower().strip()
            if key and len(key) > 2:  # Filter very short names
                if key not in unique_apps:
                    unique_apps[key] = app
                elif app.get("path", "").lower().endswith('.exe'):
                    # Prefer .exe files over other formats
                    unique_apps[key] = app
        
        return list(unique_apps.values())
    
    # ===========================================
    # WINDOWS VIRTUAL DESKTOPS INTEGRATION
    # ===========================================
    
    def create_virtual_desktop(self, desktop_name: str) -> bool:
        """Create a new Windows Virtual Desktop for environment isolation."""
        try:
            ps_command = f'''
            # Load Virtual Desktop API
            $ErrorActionPreference = "Stop"
            
            # Create new virtual desktop using Windows API
            Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                public class VirtualDesktop {{
                    [DllImport("user32.dll")]
                    public static extern IntPtr GetDesktopWindow();
                    
                    [DllImport("user32.dll")]
                    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                }}
"@
            
            # Use PowerShell cmdlets for virtual desktop management (Windows 10 v2004+)
            try {{
                # Import virtual desktop module if available
                Import-Module VirtualDesktop -ErrorAction SilentlyContinue
                New-VirtualDesktop -Name "{desktop_name}"
                Write-Output "SUCCESS: Created virtual desktop '{desktop_name}'"
            }} catch {{
                # Fallback: Create using Windows key shortcuts
                # This simulates Win+Ctrl+D to create new desktop
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("^{LWIN}d")
                Start-Sleep -Milliseconds 500
                Write-Output "SUCCESS: Created virtual desktop via shortcut"
            }}
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return "SUCCESS:" in result.stdout
            
        except Exception as e:
            print(f"Error creating virtual desktop: {e}")
            return False
    
    def switch_to_virtual_desktop(self, desktop_index: int) -> bool:
        """Switch to a specific virtual desktop by index."""
        try:
            ps_command = f'''
            # Switch to virtual desktop using Windows key shortcuts
            # Win+Ctrl+Left/Right arrows to navigate desktops
            Add-Type -AssemblyName System.Windows.Forms
            
            # Get current desktop and calculate moves needed
            $targetDesktop = {desktop_index}
            
            # Simulate Win+Ctrl+Right arrow to move to target desktop
            for ($i = 0; $i -lt $targetDesktop; $i++) {{
                [System.Windows.Forms.SendKeys]::SendWait("^{LWIN}{{RIGHT}}")
                Start-Sleep -Milliseconds 200
            }}
            
            Write-Output "SUCCESS: Switched to desktop $targetDesktop"
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return "SUCCESS:" in result.stdout
            
        except Exception as e:
            print(f"Error switching virtual desktop: {e}")
            return False
    
    def get_virtual_desktops(self) -> List[Dict[str, str]]:
        """Get list of virtual desktops."""
        try:
            ps_command = '''
            # Try to get virtual desktops info
            $ErrorActionPreference = "SilentlyContinue"
            
            try {
                # Use Virtual Desktop module if available
                Import-Module VirtualDesktop -ErrorAction SilentlyContinue
                $desktops = Get-VirtualDesktop
                foreach ($desktop in $desktops) {
                    Write-Output "Desktop|$($desktop.Name)|$($desktop.Id)"
                }
            } catch {
                # Fallback: Assume standard desktop setup
                Write-Output "Desktop|Desktop 1|primary"
                Write-Output "Desktop|Desktop 2|secondary"
            }
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            desktops = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and 'Desktop|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            desktops.append({
                                "name": parts[1].strip(),
                                "id": parts[2].strip()
                            })
            
            # Ensure at least one desktop exists
            if not desktops:
                desktops = [{"name": "Desktop 1", "id": "primary"}]
            
            return desktops
            
        except Exception as e:
            print(f"Error getting virtual desktops: {e}")
            return [{"name": "Desktop 1", "id": "primary"}]
    
    def launch_app_on_desktop(self, app_path: str, desktop_index: int = 0) -> bool:
        """Launch application on specific virtual desktop."""
        try:
            # Switch to target desktop first
            if desktop_index > 0:
                self.switch_to_virtual_desktop(desktop_index)
                time.sleep(1)  # Wait for desktop switch
            
            # Launch the application
            if app_path.startswith("shell:appsFolder"):
                # Windows Store app
                subprocess.run(["explorer", app_path], 
                             creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            elif app_path.startswith("http"):
                # Website
                subprocess.run(["start", app_path], shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            else:
                # Regular application
                subprocess.Popen([app_path],
                               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            
            return True
            
        except Exception as e:
            print(f"Error launching app on desktop: {e}")
            return False
    
    def close_desktop_apps(self, desktop_index: int) -> bool:
        """Close all applications on a specific virtual desktop."""
        try:
            # Switch to the desktop
            self.switch_to_virtual_desktop(desktop_index)
            time.sleep(1)
            
            ps_command = '''
            # Get all windows on current desktop and close them
            $ErrorActionPreference = "SilentlyContinue"
            
            # Close all windows except essential system windows
            Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | ForEach-Object {
                $processName = $_.ProcessName
                if ($processName -notin @("explorer", "dwm", "winlogon", "csrss", "lsass", "services", "smss", "wininit")) {
                    try {
                        $_.CloseMainWindow()
                        Start-Sleep -Milliseconds 100
                    } catch {}
                }
            }
            
            Write-Output "SUCCESS: Closed desktop applications"
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return "SUCCESS:" in result.stdout
            
        except Exception as e:
            print(f"Error closing desktop apps: {e}")
            return False