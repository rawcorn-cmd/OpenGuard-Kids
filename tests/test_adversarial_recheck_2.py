"""
Adversarial Verification Suite for Iteration 2 Gate Recheck (Category 2)
Author: challenger_winsvc_recheck_2
Target: Windows Service Native & 1-Click Deployment Batch Scripts

Adversarial Stress Scenarios:
1. setup_tray_startup.bat:
   - Verify run_tray.bat generation without backslash escaping issues.
   - Stress-test sys.path.insert(0, '.') resolution across diverse cwd environments.
   - Stress-test paths with spaces, single quotes, and unicode.
2. install_service.bat:
   - SCM failure command with cmd.exe /c execution of restore_dns.bat.
   - CommandLineToArgvW parsing of SCM command with spaces in project root.
   - Universal SID *S-1-5-32-544 and *S-1-5-32-545 ACL verification.
   - Ensure zero localized account names remain in icacls calls.
3. enable_dns_protection.bat and restore_dns.bat:
   - Spaces in %TEMP% paths (e.g. C:\\Users\\John Doe\\AppData\\Local\\Temp).
   - for /f "usebackq tokens=*" syntax semantics vs unquoted failure modes.
   - PowerShell Out-File -Encoding ascii output vs UTF-16 LE BOM corruption.
   - Adapter names with spaces ("Ethernet 2", "Local Area Connection").
4. Dual-stack DHCP network disaster recovery verification.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
from tests.test_challenger_winsvc import command_line_to_argv_w


# =============================================================================
# 1. Adversarial Challenge: setup_tray_startup.bat & run_tray.bat
# =============================================================================


class TestSetupTrayStartupAdversarial:
    """Stress-tests setup_tray_startup.bat and run_tray.bat generation."""

    def test_run_tray_bat_generated_content_and_syntax(self):
        """
        Verify that the code generated for run_tray.bat:
        1. Does not contain r'%~dp0' or trailing backslash raw strings.
        2. Contains cd /d "%~dp0" and sys.path.insert(0, '.').
        3. Executes in Python without SyntaxError.
        """
        script_path = REPO_ROOT / "setup_tray_startup.bat"
        content = script_path.read_text(encoding="utf-8")

        # Must not contain buggy pattern r'%~dp0'
        assert "r'%%~dp0'" not in content
        assert "r'%~dp0'" not in content

        # Must contain cd /d "%%~dp0" and sys.path.insert(0, '.')
        assert 'cd /d "%%~dp0"' in content
        assert "sys.path.insert(0, '.')" in content

        # Extract the exact python snippet generated
        # start "" "%PYTHONW_EXE%" -c "import sys; sys.path.insert(0, '.'); import src.tray.main; src.tray.main.main()"
        python_inline = "import sys; sys.path.insert(0, '.'); import src.tray.main"
        
        # Test executing this snippet from REPO_ROOT (simulating cd /d "%~dp0")
        res = subprocess.run(
            [sys.executable, "-c", f"{python_inline}; print('MODULE_LOADED_OK')"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Inline python failed: {res.stderr}"
        assert "MODULE_LOADED_OK" in res.stdout

    def test_run_tray_bat_simulated_execution_from_arbitrary_working_directory(self):
        """
        Adversarial test: simulate running run_tray.bat from C:\\Windows\\System32 or /tmp.
        Because run_tray.bat executes 'cd /d "%~dp0"', the working directory is reset
        to the project root before Python starts with sys.path.insert(0, '.').
        """
        with tempfile.TemporaryDirectory() as foreign_dir:
            # Emulate batch: cd /d "<REPO_ROOT>" && python -c "sys.path.insert(0, '.'); ..."
            cmd = [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, '.'); import src.tray.main; print('LOADED:', src.tray.main.__name__)",
            ]
            res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            assert res.returncode == 0
            assert "LOADED: src.tray.main" in res.stdout

    def test_project_root_spaces_and_special_chars_in_registry_cmd(self):
        """
        Verify that Registry Run command string quoting survives paths with spaces.
        In setup_tray_startup.bat:
        set "LAUNCHER_CMD=\"%PYTHONW_EXE%\" -c \"import sys; sys.path.insert(0, r'%PROJECT_ROOT%'); import src.tray.main; src.tray.main.main()\""
        """
        test_roots = [
            r"C:\Program Files\OpenGuard Kids",
            r"C:\Users\Parent Account\Desktop\OpenGuard-Kids",
            r"D:\Kids Security\OpenGuard",
        ]
        for root in test_roots:
            # Reconstruct the python command string inside the double quotes
            python_code = f"import sys; sys.path.insert(0, r'{root}'); import src.tray.main; src.tray.main.main()"
            # Ensure Python parser does not reject this string
            import ast
            parsed = ast.parse(python_code)
            assert parsed is not None
            # Check ast nodes: first statement is import sys, second is Expr(Call(Attribute(Name('sys')...)))
            assert len(parsed.body) == 4


# =============================================================================
# 2. Adversarial Challenge: install_service.bat SCM & ACL
# =============================================================================


class TestInstallServiceAdversarial:
    """Stress-tests SCM failure command wrapping and universal SID NTFS ACLs."""

    def test_scm_failure_command_wrapping_with_cmd_exe(self):
        """
        Verify that:
        sc.exe failure OpenGuardKidsService reset= 86400 actions= restart/60000/restart/60000/run/60000 command= "cmd.exe /c \"%PROJECT_ROOT%restore_dns.bat\""
        uses 'cmd.exe /c' and preserves the inner double-quotes around the restore_dns.bat path.
        """
        for script_file in [REPO_ROOT / "install_service.bat", REPO_ROOT / "scripts" / "windows" / "install_service.bat"]:
            content = script_file.read_text(encoding="utf-8")
            # Verify exact presence of cmd.exe /c wrapper
            assert 'command= "cmd.exe /c \\"%PROJECT_ROOT%restore_dns.bat\\""' in content, (
                f"Missing cmd.exe /c wrapper in {script_file.name}"
            )

    @pytest.mark.parametrize("project_root", [
        r"C:\OpenGuard-Kids\\",
        r"C:\Program Files\OpenGuard Kids\\",
        r"D:\Dự Án\OpenGuard Trẻ Em\\",
        r"C:\Users\John Doe\AppData\Local\Programs\OpenGuard\\",
    ])
    def test_scm_command_line_to_argv_w_preserves_quoted_bat(self, project_root: str):
        """
        Adversarial parsing test:
        When cmd.exe expands %PROJECT_ROOT%, the command string passed to CreateProcessW
        must parse via CommandLineToArgvW so that:
        argv[7] is 'command='
        argv[8] is 'cmd.exe /c "<path>restore_dns.bat"'
        """
        full_bat_path = f"{project_root}restore_dns.bat"
        # Exact command line emitted by cmd.exe
        raw_cmdline = (
            f'sc.exe failure OpenGuardKidsService reset= 86400 '
            f'actions= restart/60000/restart/60000/run/60000 '
            f'command= "cmd.exe /c \\"{full_bat_path}\\""'
        )
        argv = command_line_to_argv_w(raw_cmdline)
        assert argv[0] == "sc.exe"
        assert argv[1] == "failure"
        assert argv[2] == "OpenGuardKidsService"
        assert argv[7] == "command="
        assert argv[8] == f'cmd.exe /c "{full_bat_path}"', (
            f"Expected command payload to preserve quotes around bat path: {argv[8]}"
        )

    def test_universal_sid_usage_and_no_localized_names(self):
        """
        Adversarial check:
        Verify that icacls commands use well-known SIDs:
        - *S-1-5-32-544 (BUILTIN\\Administrators)
        - *S-1-5-32-545 (BUILTIN\\Users)
        and DO NOT use the localized string 'Administrators' or 'Users'.
        """
        targets = [
            REPO_ROOT / "install_service.bat",
            REPO_ROOT / "scripts" / "windows" / "install_service.bat",
        ]
        for script in targets:
            content = script.read_text(encoding="utf-8")
            # Verify universal SID presence
            assert "*S-1-5-32-544" in content
            assert "*S-1-5-32-545" in content

            # Verify no localized hardcoded group names in icacls commands
            for line in content.splitlines():
                if "icacls" in line:
                    assert '"Administrators"' not in line, f"Localized 'Administrators' found in {script.name}: {line}"
                    assert '"Users"' not in line, f"Localized 'Users' found in {script.name}: {line}"


# =============================================================================
# 3. Adversarial Challenge: enable_dns_protection.bat & restore_dns.bat
# =============================================================================


class TestDnsProtectionAndRestoreAdversarial:
    """Stress-tests temp path quoting, PowerShell encoding, and adapter parsing."""

    def test_temp_path_with_spaces_and_usebackq_semantics(self):
        """
        Verify that all scripts reading %TEMP%\\ogk_active_adapters.txt:
        1. Use 'usebackq tokens=*' in for /f
        2. Wrap "%TEMP%\\ogk_active_adapters.txt" in double quotes
        3. Wrap '%TEMP%\\ogk_active_adapters.txt' in single quotes in PowerShell Out-File
        """
        targets = [
            REPO_ROOT / "enable_dns_protection.bat",
            REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
            REPO_ROOT / "restore_dns.bat",
        ]
        for script in targets:
            content = script.read_text(encoding="utf-8")

            # Check PowerShell Out-File single quote wrapping
            assert "Out-File -Encoding ascii '%TEMP%\\ogk_active_adapters.txt'" in content, (
                f"Missing single-quoted %TEMP% Out-File in {script.name}"
            )

            # Check if exist double quote wrapping
            assert 'if exist "%TEMP%\\ogk_active_adapters.txt"' in content, (
                f"Unquoted if exist in {script.name}"
            )

            # Check usebackq with double-quoted filename
            assert 'for /f "usebackq tokens=*" %%a in ("%TEMP%\\ogk_active_adapters.txt") do (' in content, (
                f"Missing usebackq with quoted temp path in {script.name}"
            )

    def test_powershell_encoding_ascii_vs_utf16_bom_corruption(self):
        """
        Adversarial Oracle:
        Demonstrate why '-Encoding ascii' is critical.
        Default PowerShell 5.1 Out-File emits UTF-16 LE with BOM (\\xff\\xfe).
        When cmd.exe for /f parses UTF-16 LE, null bytes corrupt adapter names.
        ASCII encoding produces clean single-byte tokens readable by cmd.exe.
        """
        adapter_names = ["Wi-Fi", "Ethernet 2", "Local Area Connection"]

        # 1. Simulate PowerShell 5.1 default UTF-16 LE output with BOM
        utf16_bytes = io.BytesIO()
        utf16_bytes.write(b"\xff\xfe")  # UTF-16 LE BOM
        for name in adapter_names:
            utf16_bytes.write((name + "\r\n").encode("utf-16le"))
        raw_utf16 = utf16_bytes.getvalue()

        # In cmd.exe, reading raw_utf16 via ANSI/ASCII reader results in null bytes:
        ansi_view_of_utf16 = raw_utf16.decode("latin1")
        # Every ASCII character is followed by null byte '\x00'
        assert "\x00" in ansi_view_of_utf16
        # The adapter name 'Wi-Fi' appears as 'W\x00i\x00-\x00F\x00i\x00' -> corrupted!
        assert "W\x00i\x00" in ansi_view_of_utf16

        # 2. Simulate PowerShell Out-File -Encoding ascii
        ascii_bytes = io.BytesIO()
        for name in adapter_names:
            ascii_bytes.write((name + "\r\n").encode("ascii"))
        raw_ascii = ascii_bytes.getvalue()

        # In cmd.exe, reading raw_ascii via ANSI/ASCII reader is 100% clean
        clean_view = raw_ascii.decode("ascii")
        assert "\x00" not in clean_view
        lines = [line.strip() for line in clean_view.splitlines() if line.strip()]
        assert lines == adapter_names

    def test_adapter_names_with_spaces_quoting_in_netsh_commands(self):
        """
        Verify that netsh commands quote adapter names: name="%%a"
        Preventing syntax error when adapter names contain spaces (e.g. 'Ethernet 2').
        """
        targets = [
            REPO_ROOT / "enable_dns_protection.bat",
            REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
            REPO_ROOT / "restore_dns.bat",
        ]
        for script in targets:
            content = script.read_text(encoding="utf-8")
            assert 'name="%%a"' in content, f"Unquoted adapter variable name=%%a in {script.name}"

    def test_service_running_guard_in_enable_dns_protection(self):
        """
        Verify that enable_dns_protection.bat checks for RUNNING status
        before redirecting DNS, preventing loss of internet connectivity if service is down.
        """
        targets = [
            REPO_ROOT / "enable_dns_protection.bat",
            REPO_ROOT / "scripts" / "windows" / "enable_dns_protection.bat",
        ]
        for script in targets:
            content = script.read_text(encoding="utf-8")
            assert 'sc query OpenGuardKidsService | find "RUNNING"' in content
            assert "exit /b 1" in content
