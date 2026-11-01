@echo off
setlocal EnableDelayedExpansion
:: ============================================================================
:: OpenGuard Kids — One-Click Full Clean Uninstall Script
:: Purpose: Stops services, deletes SCM entries, removes Registry Run keys,
::          restores network to DHCP (IPv4 & IPv6), and purges tokens.
:: Requirements: Administrator Privileges (UAC Auto-Elevation)
:: ============================================================================

:: 1. Check Administrator Privileges and Self-Elevate via UAC
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Yeu cau quyen Administrator de go bo he thong!
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
echo   OpenGuard Kids — Go bo Toan dien va Phuc hoi Mang Ve Trang Thai Goc
echo ============================================================================

:: 3. Stop running Tray UI in user session
echo [1/5] Dung tien trinh Tray UI trong phien nguoi dung...
taskkill /F /IM pythonw.exe >nul 2>&1
echo   [OK] Da dung tien trinh Tray UI (neu co).

:: 4. Stop and delete Windows Service from SCM
echo [2/5] Dung va go bo OpenGuardKidsService khoi SCM...
net stop OpenGuardKidsService >nul 2>&1
sc.exe delete OpenGuardKidsService >nul 2>&1
echo   [OK] Da go bo OpenGuardKidsService khoi Service Control Manager.

:: 5. Remove Registry Auto-Run keys
echo [3/5] Xoa Registry Auto-Run (HKLM va HKCU)...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /f >nul 2>&1
echo   [OK] Da xoa cac muc Registry Auto-Run.

:: 6. Safety Network DNS Restore via restore_dns.bat
echo [4/5] Kich hoat phuc hoi mang an toan qua restore_dns.bat...
if exist "%PROJECT_ROOT%restore_dns.bat" (
    call "%PROJECT_ROOT%restore_dns.bat"
) else (
    echo   [INFO] restore_dns.bat khong ton tai, dung fallback truc tiep...
    netsh interface ipv4 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
    netsh interface ipv6 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
    netsh interface ipv4 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
    netsh interface ipv6 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
    netsh interface ipv4 set dnsservers name="Ethernet 2" source=dhcp >nul 2>&1
    netsh interface ipv6 set dnsservers name="Ethernet 2" source=dhcp >nul 2>&1
    ipconfig /flushdns >nul 2>&1
)
echo   [OK] Mang Internet da duoc phuc hoi DHCP dual-stack (IPv4 & IPv6).

:: 7. Clean up token and temporary files
echo [5/5] Don dep token va du lieu tam trong %ProgramData%\OpenGuardKids...
if exist "%ProgramData%\OpenGuardKids\ipc_secret.token" (
    del /F /Q "%ProgramData%\OpenGuardKids\ipc_secret.token" >nul 2>&1
)
echo   [OK] Da don dep token bao mat.

echo ============================================================================
echo   [HOAN TAT] He thong da duoc go bo hoan toan va mang Internet da phuc hoi!
echo ============================================================================
