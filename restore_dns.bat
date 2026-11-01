@echo off
setlocal EnableDelayedExpansion
:: ============================================================================
:: OpenGuard Kids — Emergency DNS Disaster Recovery Script
:: Purpose: Restores all network adapters (IPv4 & IPv6) to DHCP DNS.
:: Executed via:
::   1. 3rd SCM crash failure action (sc.exe failure)
::   2. uninstall_all.bat
::   3. Emergency administrator execution
:: ============================================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Script yeu cau dac quyen Administrator de khoi phuc DNS!
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo [OpenGuard Kids] Starting emergency DNS restoration...

:: 1. Dynamic adapter discovery via PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name | Out-File -Encoding ascii '%TEMP%\ogk_active_adapters.txt'" 2>nul
if exist "%TEMP%\ogk_active_adapters.txt" (
    for /f "usebackq tokens=*" %%a in ("%TEMP%\ogk_active_adapters.txt") do (
        echo   [+] Restoring adapter to DHCP: "%%a"
        netsh interface ipv4 set dnsservers name="%%a" source=dhcp >nul 2>&1
        netsh interface ipv6 set dnsservers name="%%a" source=dhcp >nul 2>&1
    )
    del /f /q "%TEMP%\ogk_active_adapters.txt" >nul 2>&1
)

:: 2. Static fallbacks for standard adapter names (IPv4 and IPv6)
echo   [+] Restoring Wi-Fi adapter to DHCP...
netsh interface ipv4 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
netsh interface ipv6 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1

echo   [+] Restoring Ethernet adapter to DHCP...
netsh interface ipv4 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
netsh interface ipv6 set dnsservers name="Ethernet" source=dhcp >nul 2>&1

echo   [+] Restoring Ethernet 2 adapter to DHCP...
netsh interface ipv4 set dnsservers name="Ethernet 2" source=dhcp >nul 2>&1
netsh interface ipv6 set dnsservers name="Ethernet 2" source=dhcp >nul 2>&1

:: 3. Flush DNS resolver cache
ipconfig /flushdns >nul 2>&1
echo   [OK] Windows DNS Resolver Cache flushed.

echo [OpenGuard Kids] Emergency recovery complete. Dual-stack DHCP restored.
