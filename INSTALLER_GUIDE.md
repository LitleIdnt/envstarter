# EnvStarter - Create Your Own Installer

## 🚀 Quick Build (Easiest Method)

### Step 1: Build the Executable
```bash
# Run this in Command Prompt or PowerShell
build_simple.bat
```

This will:
- Install PyInstaller automatically
- Create `dist\EnvStarter.exe` (standalone executable)
- No need for Python on target machines!

### Step 2: Test Your Executable
```bash
# Test the executable
dist\EnvStarter.exe
```

## 📦 Create Professional Installer (Optional)

If you want a proper installer like commercial software:

### Method A: NSIS Installer (Recommended)

1. **Download NSIS**: https://nsis.sourceforge.io/Download
2. **Install NSIS** (free, widely used)
3. **Run**: `installer\build_installer.bat`
4. **Get**: `EnvStarter-Setup.exe` (professional installer)

### Method B: Advanced Python Builder

1. **Run**: `python build_installer.py`
2. **Follow prompts** for full installer creation

## 🎯 What Each Method Gives You

### Simple Build (`build_simple.bat`)
- ✅ **Single .exe file** (~30MB)
- ✅ **Runs anywhere** (no Python needed)
- ✅ **Self-contained** (all dependencies included)
- ✅ **Portable** (copy and run)

### NSIS Installer (`installer\build_installer.bat`)
- ✅ **Professional installer** (like commercial software)
- ✅ **Desktop shortcut** creation
- ✅ **Start menu entry**
- ✅ **Auto-start with Windows**
- ✅ **Add/Remove Programs** entry
- ✅ **Proper uninstaller**

## 🛠️ Troubleshooting

### "pip not found"
```bash
# Make sure Python is in PATH
python -m pip install pyinstaller
```

### "PyInstaller not found"
```bash
# Install manually
pip install pyinstaller
# Then run build script again
```

### "Permission denied"
```bash
# Run Command Prompt as Administrator
# Then run the build script
```

### "Module not found" during build
```bash
# Install missing dependencies
pip install -r requirements.txt
# Then build again
```

## 📋 Distribution Guide

### For End Users (Simple)
1. Build with `build_simple.bat`
2. Share `dist\EnvStarter.exe`
3. Users double-click to run!

### For Professional Distribution
1. Create installer with NSIS
2. Share `EnvStarter-Setup.exe`
3. Users run installer for full experience

## 🎉 Your Executable Features

Both methods create a **fully functional** EnvStarter with:

- ✅ **Environment selector** with beautiful GUI
- ✅ **Application scanner** (finds Teams, Office, etc.)
- ✅ **Website launching** 
- ✅ **System tray integration**
- ✅ **Settings management**
- ✅ **Windows startup** integration
- ✅ **WCAG compliant** interface
- ✅ **Professional appearance**

## 💾 File Sizes

| Method | Size | Description |
|--------|------|-------------|
| Simple .exe | ~30MB | Standalone executable |
| NSIS Installer | ~25MB | Professional installer |
| Source Code | ~5MB | Requires Python |

## 🚀 Quick Start Commands

```bash
# Build executable (simplest)
build_simple.bat

# Test it works
dist\EnvStarter.exe

# Create installer (optional)
# 1. Install NSIS from https://nsis.sourceforge.io/
# 2. Run:
installer\build_installer.bat
```

**Your EnvStarter is ready for distribution!** 🎉