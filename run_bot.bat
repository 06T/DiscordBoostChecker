@echo off
REM Discord Boost Notification Bot - Windows Launcher
REM This script runs the Discord boost notification bot

setlocal

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Try to find Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not in your PATH.
    echo Please install Python or add it to your PATH.
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please create a .env file with your bot configuration.
    echo See README.md for setup instructions.
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
)

REM Check if discord_bot.py exists
if not exist "discord_bot.py" (
    echo [ERROR] discord_bot.py not found in current directory.
    echo Please ensure you're running this script from the Ready folder.
    echo.
    pause
    exit /b 1
)

REM Run the bot
echo ========================================
echo Discord Boost Notification Bot
echo ========================================
echo.
python run_bot.py

REM Check if Python script exited with an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Bot exited with error code %ERRORLEVEL%
    echo Check the error messages above for details.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

endlocal

