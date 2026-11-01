@echo off
:: ============================================================================
:: OpenGuard Kids — Emergency DNS Disaster Recovery Script
:: Purpose: Restores all network adapters to DHCP DNS if the service crashes.
:: Location: %ProgramFiles%\OpenGuardKids\restore_dns.bat
:: ============================================================================

echo [OpenGuard Kids] Starting emergency DNS restoration...

:: Restore Wi-Fi adapter to DHCP
netsh interface ipv4 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] Wi-Fi adapter restored to DHCP.
) else (
    echo   [INFO] Wi-Fi adapter not found or already on DHCP.
)

:: Restore Ethernet adapter to DHCP
netsh interface ipv4 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] Ethernet adapter restored to DHCP.
) else (
    echo   [INFO] Ethernet adapter not found or already on DHCP.
)

:: Restore Ethernet 2 adapter (if present)
netsh interface ipv4 set dnsservers name="Ethernet 2" source=dhcp >nul 2>&1

:: Flush DNS resolver cache
ipconfig /flushdns >nul 2>&1
echo   [OK] Windows DNS Resolver Cache flushed.

echo [OpenGuard Kids] Emergency recovery complete. Internet connectivity restored.

