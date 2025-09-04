@echo off
echo EnvStarter Installation Script
echo =============================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install dependencies
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running as Administrator or check your internet connection
    pause
    exit /b 1
)

echo.
echo Running installation test...
echo.

python test_installation.py

if %errorlevel% neq 0 (
    echo.
    echo Installation test failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo =============================
echo Installation completed successfully!
echo =============================
echo.
echo To run EnvStarter:
echo   python -m src.envstarter.main
echo.
echo Or double-click run_envstarter.bat
echo.

REM Create run script
echo @echo off > run_envstarter.bat
echo cd /d "%~dp0" >> run_envstarter.bat
echo python -m src.envstarter.main >> run_envstarter.bat
echo pause >> run_envstarter.bat

echo Created run_envstarter.bat for easy launching.
echo.
pause