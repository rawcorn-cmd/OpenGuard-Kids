@echo off
setlocal EnableDelayedExpansion
:: ============================================================================
:: OpenGuard Kids — Tray UI Startup Configuration Script
:: Purpose: Registers Tray UI in Windows Registry Run for Session 1 auto-start.
:: Requirements: Administrator Privileges (UAC Auto-Elevation)
:: ============================================================================

:: 1. Check Administrator Privileges and Self-Elevate via UAC
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Thong bao: Script yeu cau dac quyen Administrator!
    echo Dang yeu cau nang quyen qua UAC Prompt...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

:: 2. Dynamic Project Root Discovery
set "PROJECT_ROOT=%~dp0"
if exist "%~dp0src\agent\windows_service.py" (
    set "PROJECT_ROOT=%~dp0"
) else if exist "%~dp0..\..\src\agent\windows_service.py" (
    pushd "%~dp0..\.." >nul
    set "PROJECT_ROOT=%CD%\"
    popd >nul
)
:: Strip trailing backslash if present for cleaner inline python string
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

echo ============================================================================
echo   OpenGuard Kids — Dang ky Tray UI Tu Khoi Chay Khi Dang Nhap (Session 1)
echo ============================================================================

:: 3. Find pythonw.exe (windowless interpreter)
echo [1/4] Tim kiem trinh thong dich pythonw.exe (khong hien cua so console)...
set "PYTHONW_EXE="
if exist "%PROJECT_ROOT%\.venv\Scripts\pythonw.exe" (
    set "PYTHONW_EXE=%PROJECT_ROOT%\.venv\Scripts\pythonw.exe"
) else (
    where pythonw >nul 2>&1
    if %errorLevel% equ 0 (
        for /f "tokens=*" %%i in ('where pythonw') do (
            if not defined PYTHONW_EXE set "PYTHONW_EXE=%%i"
        )
    )
)

if not defined PYTHONW_EXE (
    echo   [CANH BAO] Khong tim thay pythonw.exe, thu kiem tra python.exe...
    if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
        set "PYTHONW_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    ) else (
        where python >nul 2>&1
        if %errorLevel% equ 0 (
            for /f "tokens=*" %%i in ('where python') do (
                if not defined PYTHONW_EXE set "PYTHONW_EXE=%%i"
            )
        )
    )
)

if not defined PYTHONW_EXE (
    echo [LOI] Khong tim thay Python tren he thong!
    pause
    exit /b 1
)
echo   [OK] Su dung Python: "%PYTHONW_EXE%"

:: 4. Construct launcher command with sys.path root injection
:: Prevents ModuleNotFoundError: No module named 'src' when invoked from C:\Windows\System32
set "LAUNCHER_CMD=\"%PYTHONW_EXE%\" -c \"import sys; sys.path.insert(0, r'%PROJECT_ROOT%'); import src.tray.main; src.tray.main.main()\""

:: 5. Register in Registry Auto-Run: Primary HKLM (All Users), fallback HKCU (Current User)
echo [2/4] Dang ky vao Registry Auto-Run (HKLM / HKCU)...
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /t REG_SZ /d "%LAUNCHER_CMD%" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] Da dang ky thanh cong vao HKLM Run (Kich hoat cho tat ca nguoi dung).
) else (
    echo   [CANH BAO] Khong the ghi HKLM, tien hanh ghi vao HKCU nguoi dung hien tai...
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /t REG_SZ /d "%LAUNCHER_CMD%" /f >nul 2>&1
    if %errorLevel% equ 0 (
        echo   [OK] Da ghi thanh cong vao HKCU Run cho tai khoan %USERNAME%.
    ) else (
        echo   [LOI] Khong the ghi Registry! Vui long kiem tra quyen quan tri.
    )
)

:: 6. Create standalone shortcut run_tray.bat for manual activation
echo [3/4] Tao file launcher doc lap run_tray.bat...
set "RUN_TRAY_BAT=%PROJECT_ROOT%\run_tray.bat"
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo set "PYTHONPATH=%%~dp0;%%PYTHONPATH%%"
    echo start "" "%PYTHONW_EXE%" -c "import sys; sys.path.insert(0, '.'); import src.tray.main; src.tray.main.main()"
) > "%RUN_TRAY_BAT%"
echo   [OK] File launcher: "%RUN_TRAY_BAT%"

:: 7. Launch Tray UI immediately into active user session
echo [4/4] Khoi chay ngay Tray UI trong phien lam viec hien tai...
start "" "%PYTHONW_EXE%" -c "import sys; sys.path.insert(0, r'%PROJECT_ROOT%'); import src.tray.main; src.tray.main.main()"

echo ============================================================================
echo   [HOAN TAT] Tray UI da duoc thiet lap khoi dong tu dong toan may tinh!
echo ============================================================================
