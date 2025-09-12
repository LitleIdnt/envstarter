@echo off
REM 🚀 ENVSTARTER ISOLATED LAUNCHER FOR WINDOWS 🚀
REM Creates completely isolated environments like VMs!
REM Each environment has a BIG VISIBLE NAME in the header!

echo ============================================================================
echo.
echo          🚀 ENVSTARTER - ISOLATED ENVIRONMENT LAUNCHER 🚀
echo.
echo      Each environment runs in COMPLETE ISOLATION like a VM!
echo      Environment names are shown in BIG HEADERS everywhere!
echo.
echo ============================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "isolated_launcher.py" (
    echo ❌ isolated_launcher.py not found. Please run this script from the EnvStarter directory.
    pause
    exit /b 1
)

REM Parse arguments
set ENVIRONMENT=
set MONITOR=
set LIST=

:parse_args
if "%~1"=="" goto check_action
if "%~1"=="--list" (
    set LIST=1
    shift
    goto parse_args
)
if "%~1"=="-l" (
    set LIST=1
    shift
    goto parse_args
)
if "%~1"=="--monitor" (
    set MONITOR=--monitor
    shift
    goto parse_args
)
if "%~1"=="-m" (
    set MONITOR=--monitor
    shift
    goto parse_args
)
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help
set ENVIRONMENT=%~1
shift
goto parse_args

:show_help
echo Usage: %0 [environment_name] [options]
echo.
echo Options:
echo   --list, -l      List all available environments
echo   --monitor, -m   Keep monitoring after launch
echo   --help, -h      Show this help message
echo.
echo Examples:
echo   %0                    : Interactive mode
echo   %0 "Work"             : Launch 'Work' environment
echo   %0 all                : Launch ALL environments
echo   %0 --list            : List available environments
echo   %0 "Work" --monitor  : Launch and monitor 'Work' environment
pause
exit /b 0

:check_action
REM List environments if requested
if "%LIST%"=="1" (
    echo 📋 Listing available environments...
    python isolated_launcher.py --list
    pause
    exit /b 0
)

REM Launch environment
if not "%ENVIRONMENT%"=="" (
    echo 🚀 Launching environment: %ENVIRONMENT%
    echo.
    python isolated_launcher.py "%ENVIRONMENT%" %MONITOR%
    pause
    exit /b 0
)

REM Interactive mode
echo 📋 Available environments:
python isolated_launcher.py --list
echo.
set /p env_name="Enter environment name to launch (or 'all' for all environments): "

if "%env_name%"=="" (
    echo ❌ No environment specified
    pause
    exit /b 1
)

echo.
echo 🚀 Launching environment: %env_name%
python isolated_launcher.py "%env_name%" %MONITOR%
pause