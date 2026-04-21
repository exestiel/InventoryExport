@echo off
if /i "%~1"=="__SUB__" goto :main
cd /d "%~dp0"
start "Inventory Export" cmd.exe /k call "%~f0" __SUB__
exit /b 0

:main
cd /d "%~dp0"
setlocal EnableDelayedExpansion
title Inventory Export
chcp 437 >nul 2>&1

if not exist "%~dp0source" mkdir "%~dp0source"
if not exist "%~dp0result" mkdir "%~dp0result"

set "INPUT=%~dp0source\inventory.csv"

echo.
echo ========================================
echo   Inventory Export
echo ========================================
echo.

choice /c YN /m "Has the source file already been placed in the source folder"
if errorlevel 2 (
    echo.
    echo Copy your inventory export to this exact path, then run start.bat again:
    echo   %INPUT%
    echo.
    goto :end
)

echo.
set "DEFAULT_OUT=Inventory_Final.csv"
echo Default result file: !DEFAULT_OUT!
set /p "OUTNAME=Press Enter for default, or type a different file name: "
if not defined OUTNAME set "OUTNAME=!DEFAULT_OUT!"
if "!OUTNAME!"=="" set "OUTNAME=!DEFAULT_OUT!"

for %%F in ("!OUTNAME!") do set "OUTNAME=%%~nxF"
if not defined OUTNAME (
    echo [ERROR] Invalid file name.
    goto :end
)

set "OUTPUT=%~dp0result\!OUTNAME!"

if not exist "%INPUT%" (
    echo [ERROR] Source file not found:
    echo   %INPUT%
    echo.
    echo Save your export as: source\inventory.csv
    echo.
    goto :end
)

where py >nul 2>&1
if !errorlevel! equ 0 (
    py -3 "%~dp0scripts\inventory_export.py" "%INPUT%" "!OUTPUT!"
    if errorlevel 1 (
        echo.
        echo [ERROR] Export failed.
        goto :end
    )
    goto :success
)

where python >nul 2>&1
if !errorlevel! equ 0 (
    python "%~dp0scripts\inventory_export.py" "%INPUT%" "!OUTPUT!"
    if errorlevel 1 (
        echo.
        echo [ERROR] Export failed.
        goto :end
    )
    goto :success
)

echo [ERROR] Python was not found. Install Python 3 from python.org or the Microsoft Store,
echo or ensure "py" or "python" is on your PATH.
goto :end

:success
echo.
echo Created: "!OUTPUT!"

:end
echo.
echo Press any key to close this window...
pause >nul
exit /b 0
