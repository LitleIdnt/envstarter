@echo off
title EnvStarter Installer Builder
echo.
echo ========================================
echo   ENVSTARTER INSTALLER BUILDER
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the build script
echo 🚀 Starting build process...
python build_installer.py

echo.
echo ========================================
echo Build process completed!
echo ========================================
pause