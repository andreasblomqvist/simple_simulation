@echo off
REM SimpleSim Version Bump - Quick Batch Script
REM Usage: version-bump.bat [patch|minor|major] [optional-message]

if "%1"=="" (
    echo Usage: version-bump.bat [patch^|minor^|major] [optional-message]
    echo.
    echo Examples:
    echo   version-bump.bat patch "Fix button alignment"
    echo   version-bump.bat minor "Add new simulation features" 
    echo   version-bump.bat major "Complete UI redesign"
    echo.
    echo Version Types:
    echo   patch = 0.0.1 increment ^(bug fixes, small changes^)
    echo   minor = 0.1.0 increment ^(new features, improvements^)
    echo   major = 1.0.0 increment ^(breaking changes^)
    exit /b 1
)

set BUMP_TYPE=%1
set MESSAGE=%2

echo ===========================================
echo     SimpleSim Version Bump - %BUMP_TYPE%
echo ===========================================

REM Change to project root
cd /d "%~dp0\.."

REM Call PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "scripts\version-bump.ps1" -Type %BUMP_TYPE% -Message "%MESSAGE%"

echo.
echo Version bump completed!
pause 