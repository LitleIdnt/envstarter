# Installation Guide - EnvStarter

This guide covers all installation methods and setup steps for EnvStarter.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (version 1909 or later)
- **Python**: 3.8 or higher (for source installation)
- **Memory**: 512 MB RAM
- **Storage**: 100 MB available space
- **Display**: 1024x768 resolution

### Recommended Requirements
- **Operating System**: Windows 11
- **Python**: 3.11 or higher
- **Memory**: 1 GB RAM
- **Storage**: 500 MB available space (for environments and logs)

## Installation Methods

### Method 1: From Source (Recommended for Development)

1. **Install Python 3.8+**
   - Download from [python.org](https://python.org)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/EnvStarter.git
   cd EnvStarter
   ```

3. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run EnvStarter**
   ```bash
   python -m src.envstarter.main
   ```

### Method 2: Development Installation

For developers who want to make changes:

1. **Follow steps 1-3 from Method 1**

2. **Install in Development Mode**
   ```bash
   pip install -e .
   ```

3. **Run EnvStarter**
   ```bash
   envstarter
   ```

## First-Time Setup

### Initial Launch

1. **First Run Screen**
   - EnvStarter will show the environment selector
   - Three sample environments are pre-configured
   - Select an environment to test the application

2. **System Integration Setup**
   - EnvStarter will automatically:
     - Add itself to Windows startup
     - Create a desktop shortcut
     - Install system tray icon

3. **Configuration Location**
   - Config files: `%APPDATA%\EnvStarter\`
   - Environments: `%APPDATA%\EnvStarter\environments.json`
   - Application settings: `%APPDATA%\EnvStarter\config.json`

### Verification Steps

1. **Test Environment Launch**
   - Select "Development" environment
   - Click "Launch Environment"
   - Verify applications and websites open correctly

2. **Test System Tray**
   - Click minimize or close the window
   - Check system tray for EnvStarter icon
   - Right-click icon to test context menu

3. **Test Settings**
   - Click "Settings" button
   - Navigate through all tabs
   - Try creating a new environment

## Configuration

### Windows Startup

EnvStarter automatically configures itself to start with Windows by:
- Adding registry entry to `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- This can be disabled in Settings → System → "Start with Windows"

### Desktop Shortcut

A desktop shortcut is automatically created pointing to:
- Source installation: Python script
- Executable installation: EnvStarter.exe

### System Tray Integration

The system tray icon provides:
- Quick access to environments
- Settings shortcut
- Application control (stop/exit)

## Updating

### Source Installation

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Development Installation

```bash
git pull origin main
pip install -e . --upgrade
```

## Uninstallation

### Complete Removal

1. **Stop EnvStarter**
   - Right-click system tray icon → Exit
   - Or close all EnvStarter windows

2. **Remove from Startup**
   - Run EnvStarter once
   - Go to Settings → System
   - Uncheck "Start with Windows"

3. **Remove Desktop Shortcut**
   - Settings → System → "Remove Shortcut"
   - Or manually delete from desktop

4. **Remove Configuration** (Optional)
   ```
   rmdir /s "%APPDATA%\EnvStarter"
   ```

5. **Uninstall Python Package** (If using pip installation)
   ```bash
   pip uninstall envstarter
   ```

6. **Remove Source Files** (If using source installation)
   - Delete the EnvStarter folder

## Troubleshooting Installation

### Common Issues

**Python not found:**
- Ensure Python is in PATH
- Try `py` instead of `python`
- Reinstall Python with "Add to PATH" option

**Permission errors:**
- Run Command Prompt as Administrator
- Check Windows UAC settings
- Ensure user has write permissions to installation directory

**PyQt6 installation fails:**
- Update pip: `python -m pip install --upgrade pip`
- Install Visual C++ Redistributable
- Try: `pip install PyQt6 --no-cache-dir`

**winreg module not found:**
- This is Windows-specific, ensure running on Windows
- Module should be built-in with Python on Windows

**System tray not working:**
- Check Windows notification area settings
- Ensure "Always show all icons in the notification area" is enabled
- Restart Windows Explorer process

### Verification Commands

```bash
# Check Python installation
python --version

# Check pip installation
pip --version

# Check PyQt6 installation
python -c "from PyQt6 import QtWidgets; print('PyQt6 OK')"

# Check winreg module (Windows only)
python -c "import winreg; print('winreg OK')"

# Test EnvStarter import
python -c "from src.envstarter.main import main; print('EnvStarter OK')"
```

### Log Files

If issues persist, check log files:
- **Windows**: `%APPDATA%\EnvStarter\logs\`
- Log files contain detailed error information
- Include relevant log entries when reporting issues

## Advanced Installation Options

### Custom Installation Directory

For source installations, you can place EnvStarter anywhere:

1. **Clone to desired location**
   ```bash
   git clone https://github.com/yourusername/EnvStarter.git C:\Tools\EnvStarter
   cd C:\Tools\EnvStarter
   ```

2. **Create batch file for easy access**
   ```batch
   @echo off
   cd /d C:\Tools\EnvStarter
   python -m src.envstarter.main
   ```

### Network Installation

For corporate environments:

1. **Shared Network Location**
   - Install EnvStarter to shared network drive
   - Users can run directly from network location

2. **Configuration Management**
   - Pre-configure environments in `environments.json`
   - Deploy configuration files to user AppData

### Silent Installation

For automated deployment:

```batch
@echo off
REM Silent installation script
git clone https://github.com/yourusername/EnvStarter.git %TEMP%\EnvStarter
cd %TEMP%\EnvStarter
pip install -r requirements.txt --quiet
python -m src.envstarter.main --setup-only
```

## Security Considerations

### Antivirus Software

Some antivirus software may flag EnvStarter:
- **Reason**: Application launches other programs and modifies registry
- **Solution**: Add EnvStarter to antivirus whitelist
- **Safe**: EnvStarter only launches user-configured applications

### User Permissions

EnvStarter requires:
- **Registry write access**: For Windows startup integration
- **File system access**: For configuration and logs
- **Network access**: For opening websites (not for data transmission)

### Data Privacy

EnvStarter:
- **Local only**: All data stored locally on user machine
- **No telemetry**: No usage data transmitted
- **No account required**: Fully offline operation