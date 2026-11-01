@echo off
setlocal EnableDelayedExpansion
:: ============================================================================
:: OpenGuard Kids — DNS Protection Activation Script
:: Location: scripts/windows/enable_dns_protection.bat
:: Purpose: Redirects active network adapters to local DNS Proxy (127.0.0.1)
::          and prevents IPv6 leaks by binding IPv6 DNS to loopback (::1).
:: Requirements: OpenGuardKidsService must be RUNNING. Administrator Privileges.
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
echo   OpenGuard Kids — Kich hoat Bao ve Mang va Loc Ten Mien (DNS Protection)
echo ============================================================================

:: 3. Prerequisite Guard: OpenGuardKidsService must be RUNNING
echo [1/3] Kiem tra trang thai dich vu OpenGuardKidsService...
sc query OpenGuardKidsService | find "RUNNING" >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [LOI NGHIEP VU] OpenGuardKidsService chua duoc khoi chay!
    echo De tranh mat ket noi Internet, he thong khong the chuyen huong DNS.
    echo Vui long chay "install_service.bat" hoac "net start OpenGuardKidsService" truoc.
    echo.
    pause
    exit /b 1
)
echo   [OK] Dich vu dang hoat dong o trang thai RUNNING.

:: 4. Dynamic Adapter Discovery and DNS Configuration
echo [2/3] Cau hinh DNS 127.0.0.1 (IPv4) va ::1 (IPv6 Loopback)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name | Out-File -Encoding ascii '%TEMP%\ogk_active_adapters.txt'" 2>nul
if exist "%TEMP%\ogk_active_adapters.txt" (
    for /f "usebackq tokens=*" %%a in ("%TEMP%\ogk_active_adapters.txt") do (
        echo   [+] Cau hinh adapter: "%%a"
        netsh interface ipv4 set dnsservers name="%%a" source=static address=127.0.0.1 register=none validate=no >nul 2>&1
        netsh interface ipv6 set dnsservers name="%%a" source=static address=::1 register=none validate=no >nul 2>&1
    )
    del /f /q "%TEMP%\ogk_active_adapters.txt" >nul 2>&1
)

:: Static fallbacks for standard adapter names
netsh interface ipv4 set dnsservers name="Wi-Fi" source=static address=127.0.0.1 register=none validate=no >nul 2>&1
netsh interface ipv6 set dnsservers name="Wi-Fi" source=static address=::1 register=none validate=no >nul 2>&1
netsh interface ipv4 set dnsservers name="Ethernet" source=static address=127.0.0.1 register=none validate=no >nul 2>&1
netsh interface ipv6 set dnsservers name="Ethernet" source=static address=::1 register=none validate=no >nul 2>&1
netsh interface ipv4 set dnsservers name="Ethernet 2" source=static address=127.0.0.1 register=none validate=no >nul 2>&1
netsh interface ipv6 set dnsservers name="Ethernet 2" source=static address=::1 register=none validate=no >nul 2>&1

:: 5. Flush Resolver Cache
echo [3/3] Lam sach bo nho dem DNS Windows (ipconfig /flushdns)...
ipconfig /flushdns >nul 2>&1
echo   [OK] Windows DNS Resolver Cache da duoc lam moi.

echo ============================================================================
echo   [HOAN TAT] Che do bao ve mang DNS Protection da duoc bat thanh cong!
echo ============================================================================
