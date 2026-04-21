@echo off
cd /d "%~dp0"
if not exist "%~dp0source" mkdir "%~dp0source"
if not exist "%~dp0result" mkdir "%~dp0result"
set "INPUT=%~dp0source\inventory.csv"
set "OUTPUT=%~dp0result\Inventory_Final.csv"

where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3 "%~dp0scripts\inventory_export.py" "%INPUT%" "%OUTPUT%"
    exit /b %errorlevel%
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    python "%~dp0scripts\inventory_export.py" "%INPUT%" "%OUTPUT%"
    exit /b %errorlevel%
)

echo [ERROR] Python was not found. Install Python 3.11+ or add py/python to PATH.
exit /b 1
