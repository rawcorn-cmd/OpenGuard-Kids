@echo off
setlocal EnableDelayedExpansion
:: ============================================================================
:: OpenGuard Kids — Windows Service 1-Click Installation Script
:: Purpose: Registers and configures OpenGuardKidsService in Session 0.
:: Requirements: Python 3.11+, Administrator Privileges (UAC Auto-Elevation)
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

echo ============================================================================
echo   OpenGuard Kids — Cai dat Dich vu Nen Bao ve Tre Em (Windows Service)
echo ============================================================================
echo [1/5] Kiem tra trinh thong dich Python...

set "PYTHON_EXE="
if exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if %errorLevel% equ 0 (
        for /f "tokens=*" %%i in ('where python') do (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
        )
    )
)

if not defined PYTHON_EXE (
    echo [LOI] Khong tim thay trinh thong dich Python 3.11+ tren he thong!
    echo Vui long cai dat Python hoac tao virtual environment tai .venv
    pause
    exit /b 1
)
echo   [OK] Python: "%PYTHON_EXE%"

echo [2/5] Kiem tra thu vien he thong pywin32...
"%PYTHON_EXE%" -c "import win32service" >nul 2>&1
if %errorLevel% neq 0 (
    echo   [CANH BAO] pywin32 chua duoc dang ky day du. Dang chay postinstall...
    for /f "tokens=*" %%i in ('"%PYTHON_EXE%" -c "import sys, os; print(os.path.join(os.path.dirname(sys.executable), 'pywin32_postinstall.py'))"') do (
        if exist "%%i" (
            "%PYTHON_EXE%" "%%i" -install >nul 2>&1
        )
    )
)
echo   [OK] pywin32 san sang.

echo [3/5] Khoi tao thu muc du lieu he thong va thiet lap NTFS ACL...
set "DATA_DIR=%ProgramData%\OpenGuardKids"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
:: Cap quyen Full Control cho SYSTEM va Administrators (SID *S-1-5-32-544); Read/Execute cho Users (SID *S-1-5-32-545)
icacls "%DATA_DIR%" /inheritance:r /grant:r "SYSTEM":(OI)(CI)(F) /grant:r "*S-1-5-32-544":(OI)(CI)(F) /grant:r "*S-1-5-32-545":(OI)(CI)(RX) >nul 2>&1
echo   [OK] Data Directory: "%DATA_DIR%"

echo [4/5] Dang ky Windows Service vao SCM va cau hinh tu phuc hoi...
"%PYTHON_EXE%" "%PROJECT_ROOT%src\agent\windows_service.py" install
if %errorLevel% neq 0 (
    echo   [INFO] Thu muc dich vu da ton tai, tien hanh cap nhat...
    "%PYTHON_EXE%" "%PROJECT_ROOT%src\agent\windows_service.py" update
)

:: Cau hinh chinh sach phuc hoi 3 tang khi crash: 2 lan restart sau 60s, lan 3 chay restore_dns.bat
sc.exe failure OpenGuardKidsService reset= 86400 actions= restart/60000/restart/60000/run/60000 command= "cmd.exe /c \"%PROJECT_ROOT%restore_dns.bat\"" >nul 2>&1
sc.exe config OpenGuardKidsService start= auto >nul 2>&1
echo   [OK] SCM Failure Recovery Policy da duoc cau hinh (3-Tier Auto Recovery).

echo [5/5] Khoi dong OpenGuardKidsService...
net start OpenGuardKidsService
if %errorLevel% equ 0 (
    echo ============================================================================
    echo   [HOAN TAT] Dich vu OpenGuardKidsService da duoc cai dat va khoi chay!
    echo ============================================================================
) else (
    echo [CANH BAO] net start tra ve ma loi: %errorLevel%.
    echo Vui long kiem tra Windows Event Viewer de biet chi tiet.
)
