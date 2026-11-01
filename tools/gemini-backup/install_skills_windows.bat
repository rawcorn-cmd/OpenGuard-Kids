@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   OpenGuard Kids - Setup Gemini / Antigravity Skills
echo ========================================================
echo.

set TARGET_DIR=%USERPROFILE%\.gemini\config\skills
echo [*] Target directory: !TARGET_DIR!

if not exist "!TARGET_DIR!" (
    echo [*] Creating target directory...
    mkdir "!TARGET_DIR!"
)

echo [*] Copying custom skills...
xcopy /E /I /Y "%~dp0skills\*" "!TARGET_DIR!\"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All custom skills have been installed to:
    echo           !TARGET_DIR!
) else (
    echo.
    echo [ERROR] Failed to copy skills. Please check permissions.
)

echo.
pause
