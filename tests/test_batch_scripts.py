"""
Static Analysis and AST Validation Test Suite for OpenGuard Kids Windows Batch Scripts
Validates:
- install_service.bat (root & scripts/windows/)
- enable_dns_protection.bat (root & scripts/windows/)
- setup_tray_startup.bat (root & scripts/windows/)
- uninstall_all.bat (root & scripts/windows/)
- restore_dns.bat

Safety:
Zero destructive commands are executed on the host. Tests statically parse,
tokenize, and validate commands, syntax integrity, and parameter specifications.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

ROOT_BATCH_FILES = [
    REPO_ROOT / "install_service.bat",
    REPO_ROOT / "enable_dns_protection.bat",
    REPO_ROOT / "setup_tray_startup.bat",
    REPO_ROOT / "uninstall_all.bat",
    REPO_ROOT / "restore_dns.bat",
]

SCRIPTS_WINDOWS_BATCH_FILES = [
    REPO_ROOT / "scripts" / "windows" / "install_service.bat",
    REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
    REPO_ROOT / "scripts" / "windows" / "setup_tray_startup.bat",
    REPO_ROOT / "scripts" / "windows" / "uninstall_all.bat",
]

ALL_BATCH_FILES = ROOT_BATCH_FILES + SCRIPTS_WINDOWS_BATCH_FILES


def test_batch_scripts_exist_and_non_empty():
    """Verify that all 4 scripts + restore_dns.bat exist in root and scripts/windows/."""
    for script_path in ALL_BATCH_FILES:
        assert script_path.is_file(), f"Batch script missing: {script_path}"
        content = script_path.read_text(encoding="utf-8", errors="replace")
        assert len(content.strip()) > 50, f"Batch script empty: {script_path}"


def test_uac_self_elevation_pattern_across_all_scripts():
    """Verify standard UAC elevation check and PowerShell relaunch in all scripts."""
    elevation_cmd = "net session >nul 2>&1"
    runas_cmd = "Start-Process -FilePath '%~f0' -Verb RunAs"
    cd_cmd = 'cd /d "%~dp0"'

    for script_path in ALL_BATCH_FILES:
        content = script_path.read_text(encoding="utf-8", errors="replace")
        assert elevation_cmd in content, (
            f"Missing 'net session' UAC check in {script_path.name}"
        )
        assert runas_cmd in content, (
            f"Missing PowerShell RunAs elevation in {script_path.name}"
        )
        assert cd_cmd in content, (
            f"Missing 'cd /d \"%~dp0\"' directory normalization in {script_path.name}"
        )


def test_dynamic_project_root_discovery():
    """Verify dynamic root detection in scripts so they run in root or subfolder."""
    for script_path in ALL_BATCH_FILES:
        if script_path.name == "restore_dns.bat":
            continue
        content = script_path.read_text(encoding="utf-8", errors="replace")
        assert 'set "PROJECT_ROOT=%~dp0"' in content
        assert "windows_service.py" in content


def test_install_service_script_scm_and_acl_configuration():
    """Verify install_service.bat SCM registration, recovery, and NTFS ACL."""
    targets = [
        REPO_ROOT / "install_service.bat",
        REPO_ROOT / "scripts" / "windows" / "install_service.bat",
    ]
    for script_path in targets:
        content = script_path.read_text(encoding="utf-8", errors="replace")

        # Python interpreter detection
        assert ".venv\\Scripts\\python.exe" in content
        assert "where python" in content

        # pywin32 check
        assert "import win32service" in content
        assert "pywin32_postinstall.py" in content

        # NTFS ACL with SID *S-1-5-32-545
        assert "%ProgramData%\\OpenGuardKids" in content
        assert "icacls" in content
        assert "*S-1-5-32-544" in content
        assert "*S-1-5-32-545" in content
        assert "(OI)(CI)(RX)" in content
        assert '"SYSTEM":(OI)(CI)(F)' in content
        assert '"*S-1-5-32-544":(OI)(CI)(F)' in content

        # Windows Service installation and update fallback
        assert "windows_service.py" in content
        assert "install" in content
        assert "update" in content

        # SCM failure auto-recovery policy (2 restarts after 60s, 3rd runs restore_dns.bat)
        assert "sc.exe failure OpenGuardKidsService" in content
        assert "reset= 86400" in content
        assert "actions= restart/60000/restart/60000/run/60000" in content
        assert 'command= "cmd.exe /c' in content
        assert "restore_dns.bat" in content
        assert "sc.exe config OpenGuardKidsService start= auto" in content

        # Service start
        assert "net start OpenGuardKidsService" in content


def test_enable_dns_protection_script_guard_and_dual_stack():
    """Verify enable_dns_protection.bat prerequisite guard and dual-stack DNS setup."""
    targets = [
        REPO_ROOT / "enable_dns_protection.bat",
        REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
    ]
    for script_path in targets:
        content = script_path.read_text(encoding="utf-8", errors="replace")

        # Service RUNNING prerequisite guard
        assert 'sc query OpenGuardKidsService | find "RUNNING"' in content
        assert "exit /b 1" in content

        # PowerShell active physical adapter discovery
        assert "Get-NetAdapter -Physical" in content
        assert "$_.Status -eq 'Up'" in content
        assert "Out-File -Encoding" in content
        assert 'for /f "usebackq tokens=*"' in content
        assert 'in ("%TEMP%\\ogk_active_adapters.txt")' in content

        # IPv4 DNS redirection to 127.0.0.1
        assert "source=static address=127.0.0.1" in content
        assert "netsh interface ipv4 set dnsservers" in content

        # IPv6 DNS leak prevention by pointing to ::1
        assert "source=static address=::1" in content
        assert "netsh interface ipv6 set dnsservers" in content

        # Static adapter fallbacks
        assert 'name="Wi-Fi"' in content
        assert 'name="Ethernet"' in content
        assert 'name="Ethernet 2"' in content

        # Resolver cache flush
        assert "ipconfig /flushdns" in content


def test_setup_tray_startup_script_and_registry_run():
    """Verify setup_tray_startup.bat windowless interpreter, sys.path injection, and Registry."""
    targets = [
        REPO_ROOT / "setup_tray_startup.bat",
        REPO_ROOT / "scripts" / "windows" / "setup_tray_startup.bat",
    ]
    for script_path in targets:
        content = script_path.read_text(encoding="utf-8", errors="replace")

        # Windowless pythonw detection
        assert "pythonw" in content

        # sys.path root injection for Session 0 / System32 isolation fix
        assert "sys.path.insert(0" in content
        assert "src.tray.main" in content

        # Registry Auto-Run keys (HKLM with HKCU fallback)
        assert "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" in content
        assert "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" in content
        assert '"OpenGuardKidsTray"' in content

        # Standalone run_tray.bat creation
        assert "run_tray.bat" in content
        assert "r'%%~dp0'" not in content, (
            f"Forbidden r'%%~dp0' in {script_path.name}: trailing backslash breaks Python raw string"
        )
        assert "sys.path.insert(0, '.')" in content

        # Immediate launch into active user session
        assert 'start ""' in content


def test_uninstall_all_script_clean_teardown():
    """Verify uninstall_all.bat process termination, service removal, registry cleanup, DHCP."""
    targets = [
        REPO_ROOT / "uninstall_all.bat",
        REPO_ROOT / "scripts" / "windows" / "uninstall_all.bat",
    ]
    for script_path in targets:
        content = script_path.read_text(encoding="utf-8", errors="replace")

        # Kill running Tray UI
        assert "taskkill /F /IM pythonw.exe" in content

        # Stop and delete Windows Service
        assert "net stop OpenGuardKidsService" in content
        assert "sc.exe delete OpenGuardKidsService" in content

        # Delete Registry Auto-Run keys
        assert 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "OpenGuardKidsTray"' in content
        assert 'reg delete "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "OpenGuardKidsTray"' in content

        # Restore DNS via restore_dns.bat
        assert "restore_dns.bat" in content
        assert "source=dhcp" in content

        # Token cleanup
        assert "ipc_secret.token" in content


def test_restore_dns_script_dual_stack_dhcp_restoration():
    """Verify restore_dns.bat restores both IPv4 and IPv6 to DHCP and flushes DNS."""
    script_path = REPO_ROOT / "restore_dns.bat"
    content = script_path.read_text(encoding="utf-8", errors="replace")

    # UAC elevation check
    assert "net session >nul 2>&1" in content

    # Dynamic adapter query
    assert "Get-NetAdapter -Physical" in content
    assert "Out-File -Encoding" in content
    assert 'for /f "usebackq tokens=*"' in content
    assert 'in ("%TEMP%\\ogk_active_adapters.txt")' in content

    # IPv4 DHCP restoration
    assert 'netsh interface ipv4 set dnsservers name="Wi-Fi" source=dhcp' in content
    assert 'netsh interface ipv4 set dnsservers name="Ethernet" source=dhcp' in content
    assert 'netsh interface ipv4 set dnsservers name="Ethernet 2" source=dhcp' in content

    # IPv6 DHCP restoration
    assert 'netsh interface ipv6 set dnsservers name="Wi-Fi" source=dhcp' in content
    assert 'netsh interface ipv6 set dnsservers name="Ethernet" source=dhcp' in content
    assert 'netsh interface ipv6 set dnsservers name="Ethernet 2" source=dhcp' in content

    # Flush DNS cache
    assert "ipconfig /flushdns" in content


def test_batch_syntax_and_quote_integrity():
    """Verify balanced parentheses and quotes across all batch blocks."""
    for script_path in ALL_BATCH_FILES:
        lines = script_path.read_text(encoding="utf-8", errors="replace").splitlines()

        paren_depth = 0
        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            # Skip pure comments
            if line.startswith("::") or line.startswith("REM ") or not line:
                continue

            # In Windows batch, paired double quotes balance on single lines
            quote_count = line.count('"')
            assert quote_count % 2 == 0, (
                f"Unbalanced double-quotes in {script_path.name}:{line_no} -> {line}"
            )

            # Track block parenthesis balance
            paren_depth += line.count("(") - line.count(")")
            assert paren_depth >= 0, (
                f"Negative parenthesis depth in {script_path.name}:{line_no} -> {line}"
            )

        assert paren_depth == 0, (
            f"Unbalanced parentheses at EOF in {script_path.name} (remaining: {paren_depth})"
        )


def test_dynamic_adapter_discovery_encoding_and_temp_quoting():
    """Verify Out-File encoding and usebackq quoted temp file across all dynamic adapter scripts."""
    scripts_with_dynamic_discovery = [
        REPO_ROOT / "enable_dns_protection.bat",
        REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
        REPO_ROOT / "restore_dns.bat",
    ]
    for script_path in scripts_with_dynamic_discovery:
        content = script_path.read_text(encoding="utf-8", errors="replace")
        assert "Out-File -Encoding" in content, (
            f"Missing 'Out-File -Encoding' in {script_path.name}"
        )
        assert 'for /f "usebackq tokens=*"' in content, (
            f"Missing 'for /f \"usebackq tokens=*\"' in {script_path.name}"
        )
        assert 'in ("%TEMP%\\ogk_active_adapters.txt")' in content, (
            f"Missing quoted temp file 'in (\"%TEMP%\\ogk_active_adapters.txt\")' in {script_path.name}"
        )

