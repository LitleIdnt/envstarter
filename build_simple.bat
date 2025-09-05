@echo off
title EnvStarter Builder
echo.
echo ========================================
echo   ENVSTARTER SIMPLE BUILDER
echo ========================================
echo.

REM Install PyInstaller first
echo 🔄 Installing PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyInstaller
    echo Try running as Administrator or check your Python installation
    pause
    exit /b 1
)

echo ✅ PyInstaller installed successfully
echo.

REM Create the executable
echo 🚀 Creating EnvStarter.exe...
pyinstaller --onefile --windowed --name EnvStarter --icon=resources\envstarter_icon.ico --add-data="src;src" --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtWidgets --hidden-import PyQt6.QtGui --hidden-import pystray --hidden-import PIL --hidden-import psutil EnvStarter.py

if %errorlevel% neq 0 (
    echo ❌ Failed to create executable
    pause
    exit /b 1
)

echo.
echo ✅ Executable created successfully!
echo 📦 Location: dist\EnvStarter.exe

REM Check if executable exists
if exist "dist\EnvStarter.exe" (
    echo.
    echo 🎉 BUILD COMPLETE!
    echo.
    echo Your standalone EnvStarter.exe is ready at:
    echo    %CD%\dist\EnvStarter.exe
    echo.
    echo You can now:
    echo 1. Run dist\EnvStarter.exe directly
    echo 2. Copy it anywhere and run it
    echo 3. Create shortcuts to it
    echo 4. Distribute it to other computers
    echo.
    echo The .exe file contains everything needed to run!
    echo.
) else (
    echo ❌ Executable was not created
)

pause