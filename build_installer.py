"""
Build script to create EnvStarter installer.
This script creates a Windows installer (.msi) for EnvStarter.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error {description}:")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True

def create_executable():
    """Create standalone executable using PyInstaller."""
    print("\n" + "="*50)
    print("🚀 CREATING ENVSTARTER EXECUTABLE")
    print("="*50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        if not run_command(["pip", "install", "pyinstaller"], "Installing PyInstaller"):
            return False
    
    # Create build directory
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name", "EnvStarter",         # Executable name
        "--icon", "resources/envstarter_icon.ico",  # Icon (if exists)
        "--add-data", "src;src",        # Include source code
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtWidgets", 
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--hidden-import", "psutil",
        "EnvStarter.py"                 # Main script
    ]
    
    # Remove icon if file doesn't exist
    icon_path = Path("resources/envstarter_icon.ico")
    if not icon_path.exists():
        print("⚠️ Icon file not found, creating without icon")
        cmd.remove("--icon")
        cmd.remove("resources/envstarter_icon.ico")
    
    if not run_command(cmd, "Creating executable with PyInstaller"):
        return False
    
    exe_path = Path("dist/EnvStarter.exe")
    if exe_path.exists():
        print(f"✅ Executable created: {exe_path.absolute()}")
        print(f"📦 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print("❌ Executable not found after build")
        return False

def create_installer_files():
    """Create installer configuration files."""
    print("\n" + "="*50) 
    print("📄 CREATING INSTALLER FILES")
    print("="*50)
    
    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # WiX installer configuration
    wix_config = '''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="EnvStarter" 
           Language="1033" 
           Version="1.0.0" 
           Manufacturer="EnvStarter Team" 
           UpgradeCode="12345678-1234-1234-1234-123456789012">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perUser" 
             Description="Start your perfect work environment with one click" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="EnvStarter" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="LocalAppDataFolder">
        <Directory Id="INSTALLFOLDER" Name="EnvStarter" />
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="EnvStarter"/>
      </Directory>
      <Directory Id="DesktopFolder" Name="Desktop" />
      <Directory Id="StartupFolder" Name="Startup" />
    </Directory>
    
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="EnvStarterExe" Guid="*">
        <File Id="EnvStarterExe" 
              Source="$(var.SourceDir)\\dist\\EnvStarter.exe" 
              KeyPath="yes" />
        
        <!-- Desktop shortcut -->
        <Shortcut Id="DesktopShortcut"
                  Directory="DesktopFolder"
                  Name="EnvStarter"
                  Description="Start your perfect work environment"
                  Target="[INSTALLFOLDER]EnvStarter.exe"
                  WorkingDirectory="INSTALLFOLDER" />
        
        <!-- Start Menu shortcut -->
        <Shortcut Id="StartMenuShortcut"
                  Directory="ApplicationProgramsFolder"
                  Name="EnvStarter"
                  Description="Start your perfect work environment"
                  Target="[INSTALLFOLDER]EnvStarter.exe"
                  WorkingDirectory="INSTALLFOLDER" />
        
        <!-- Registry entry for auto-start (optional) -->
        <RegistryValue Root="HKCU" 
                       Key="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" 
                       Name="EnvStarter" 
                       Type="string" 
                       Value="[INSTALLFOLDER]EnvStarter.exe"
                       KeyPath="no" />
      </Component>
    </ComponentGroup>
    
    <!-- Remove desktop shortcut on uninstall -->
    <DirectoryRef Id="DesktopFolder">
      <Component Id="DesktopShortcutComponent" Guid="*">
        <RemoveFolder Id="DesktopShortcutFolder" On="uninstall" />
        <RegistryValue Root="HKCU" 
                       Key="Software\\EnvStarter\\Install" 
                       Name="DesktopShortcut" 
                       Type="integer" 
                       Value="1" 
                       KeyPath="yes" />
      </Component>
    </DirectoryRef>
    
  </Product>
</Wix>'''
    
    wix_file = installer_dir / "EnvStarter.wxs"
    with open(wix_file, 'w', encoding='utf-8') as f:
        f.write(wix_config)
    
    print(f"✅ WiX config created: {wix_file}")
    
    # NSIS installer script (alternative)
    nsis_script = '''
!define APPNAME "EnvStarter"
!define COMPANYNAME "EnvStarter Team" 
!define DESCRIPTION "Start your perfect work environment with one click"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/envstarter/envstarter"
!define UPDATEURL "https://github.com/envstarter/envstarter/releases"
!define ABOUTURL "https://github.com/envstarter/envstarter"
!define INSTALLSIZE 50000

RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\\${APPNAME}"
Name "${APPNAME}"
Icon "resources\\envstarter_icon.ico"
outFile "EnvStarter-Setup.exe"

!include LogicLib.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" 
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
functionEnd

section "install"
    setOutPath $INSTDIR
    file "dist\\EnvStarter.exe"
    
    # Desktop shortcut
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\EnvStarter.exe" "" "$INSTDIR\\EnvStarter.exe" 0
    
    # Start menu
    createDirectory "$SMPROGRAMS\\${APPNAME}"
    createShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\EnvStarter.exe" "" "$INSTDIR\\EnvStarter.exe" 0
    createShortCut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe" "" "$INSTDIR\\uninstall.exe" 0
    
    # Auto-start registry entry (optional)
    writeRegStr HKCU "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" "${APPNAME}" "$INSTDIR\\EnvStarter.exe"
    
    # Uninstaller
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    # Registry entries for Add/Remove Programs
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "HelpLink" "${HELPURL}"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    writeRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    writeRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    writeRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    writeRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
    writeRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
    writeRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
sectionEnd

section "uninstall"
    # Remove files
    delete "$INSTDIR\\EnvStarter.exe"
    delete "$INSTDIR\\uninstall.exe"
    rmDir "$INSTDIR"
    
    # Remove shortcuts
    delete "$DESKTOP\\${APPNAME}.lnk"
    delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    delete "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk"
    rmDir "$SMPROGRAMS\\${APPNAME}"
    
    # Remove auto-start
    deleteRegValue HKCU "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" "${APPNAME}"
    
    # Remove uninstaller information from the registry
    deleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
sectionEnd
'''
    
    nsis_file = installer_dir / "EnvStarter.nsi"
    with open(nsis_file, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print(f"✅ NSIS script created: {nsis_file}")
    
    # Batch script to build installer
    build_script = '''@echo off
echo Building EnvStarter Installer...

REM Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NSIS not found. Please install NSIS from https://nsis.sourceforge.io/
    echo Download and install NSIS, then run this script again.
    pause
    exit /b 1
)

REM Build the installer
makensis EnvStarter.nsi

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Installer created successfully!
    echo 📦 Location: EnvStarter-Setup.exe
    echo.
    echo The installer includes:
    echo - EnvStarter application
    echo - Desktop shortcut
    echo - Start menu entry  
    echo - Auto-start with Windows
    echo - Proper uninstaller
    echo.
) else (
    echo ❌ Error creating installer
)

pause
'''
    
    build_bat = installer_dir / "build_installer.bat"
    with open(build_bat, 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print(f"✅ Build script created: {build_bat}")
    
    return True

def create_icon_if_missing():
    """Create a simple icon if it doesn't exist."""
    icon_path = Path("resources/envstarter_icon.ico")
    
    if icon_path.exists():
        print(f"✅ Icon already exists: {icon_path}")
        return True
    
    print("🎨 Creating simple icon...")
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple 32x32 icon
        size = 32
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple green circle with arrow
        draw.ellipse([4, 4, 28, 28], fill=(40, 167, 69, 255), outline=(33, 136, 56, 255), width=2)
        
        # Arrow pointing right
        arrow_points = [(12, 10), (20, 16), (12, 22), (15, 16)]
        draw.polygon(arrow_points, fill=(255, 255, 255, 255))
        
        # Ensure directory exists
        icon_path.parent.mkdir(exist_ok=True)
        
        # Save as ICO
        img.save(icon_path, "ICO")
        print(f"✅ Icon created: {icon_path}")
        return True
        
    except ImportError:
        print("⚠️ PIL not available, skipping icon creation")
        return False
    except Exception as e:
        print(f"⚠️ Error creating icon: {e}")
        return False

def main():
    """Main build function."""
    print("🚀 ENVSTARTER INSTALLER BUILDER")
    print("="*60)
    
    # Step 1: Create icon if missing
    create_icon_if_missing()
    
    # Step 2: Create executable
    if not create_executable():
        print("\n❌ Failed to create executable")
        return False
    
    # Step 3: Create installer files
    if not create_installer_files():
        print("\n❌ Failed to create installer files")
        return False
    
    print("\n" + "="*60)
    print("🎉 BUILD COMPLETE!")
    print("="*60)
    print("\n📦 Next steps:")
    print("1. Install NSIS from: https://nsis.sourceforge.io/Download")
    print("2. Run: installer\\build_installer.bat")
    print("3. Your installer will be: installer\\EnvStarter-Setup.exe")
    print("\n✨ Installer features:")
    print("   ✅ Desktop shortcut")
    print("   ✅ Start menu entry")
    print("   ✅ Auto-start with Windows")
    print("   ✅ Proper Add/Remove Programs entry")
    print("   ✅ Clean uninstaller")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)