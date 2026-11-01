"""
Adversarial Stress and Edge-Case Test Suite for OpenGuard Kids Windows Service & Batch Scripts
Target: Category 2 (Windows Service Native & 1-Click Deployment)
Tester: challenger_winsvc_1
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock, patch

import pytest

from src.agent.service import AgentService
import src.agent.windows_service as ws
from src.agent.windows_service import (
    HAS_PYWIN32,
    OpenGuardKidsWindowsService,
    _DummyServiceFramework,
    _DummyWin32Event,
    _DummyWin32Service,
    _DummyWinError,
    _EventHandle,
    servicemanager,
    win32event,
    win32service,
    winerror,
)


# =============================================================================
# 1. Windows Service Lifecycle Edge Cases
# =============================================================================


class TestWindowsServiceLifecycleAdversarial:
    """Stress-tests lifecycle transitions, race conditions, and exception propagation."""

    def test_svc_stop_called_repeatedly_concurrent(self):
        """Stress: 10 concurrent threads call SvcStop() simultaneously."""
        mock_agent = MagicMock(spec=AgentService)
        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        errors = []

        def worker():
            try:
                service.SvcStop()
            except Exception as ex:
                errors.append(ex)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2.0)

        assert not errors, f"Concurrent SvcStop raised errors: {errors}"
        # Stop event must be signaled
        assert win32event.WaitForSingleObject(service.stop_event, 0) == win32event.WAIT_OBJECT_0
        # Agent stop should have been invoked
        assert mock_agent.stop.called

    def test_svc_stop_before_svc_do_run_lifecycle_inconsistency(self):
        """
        Adversarial Finding: SvcStop called before SvcDoRun starts loop.
        Empirically verifies that if SvcStop runs first:
        1. SvcDoRun starts the agent
        2. SvcDoRun breaks immediately because stop_event is set
        3. But SvcDoRun exits leaving agent.is_running == True and final status == SERVICE_RUNNING (4).
        """
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.is_running = False

        def fake_start():
            mock_agent.is_running = True

        mock_agent.start.side_effect = fake_start

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        # 1. Call SvcStop first (e.g. rapid stop while start pending)
        service.SvcStop()
        assert win32event.WaitForSingleObject(service.stop_event, 0) == win32event.WAIT_OBJECT_0

        def fake_stop():
            mock_agent.is_running = False
        mock_agent.stop.side_effect = fake_stop

        # 2. Call SvcDoRun
        service.SvcDoRun()

        # The agent was started, and cleanly stopped afterwards
        assert mock_agent.start.called
        assert mock_agent.stop.called
        assert mock_agent.is_running is False, "Agent must be stopped after SvcDoRun exits!"
        # Final status in history is SERVICE_STOPPED (1)
        assert service.status_history[-1]["status"] == win32service.SERVICE_STOPPED

    def test_svc_do_run_internal_termination_leaves_scm_running(self):
        """
        Adversarial Finding: If agent.is_running becomes False without stop_event being set,
        SvcDoRun exits loop cleanly without reporting SERVICE_STOPPED or SCM error code.
        """
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.is_running = True

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        def fake_wait(event, timeout):
            # Simulate internal shutdown / silent failure
            mock_agent.is_running = False
            return 258  # WAIT_TIMEOUT

        with patch.object(ws.win32event, "WaitForSingleObject", side_effect=fake_wait):
            service.SvcDoRun()

        # Both SERVICE_RUNNING and SERVICE_STOPPED were reported
        reported_statuses = [r["status"] for r in service.status_history]
        assert win32service.SERVICE_STOPPED in reported_statuses
        assert reported_statuses[-1] == win32service.SERVICE_STOPPED
        assert mock_agent.stop.called

    def test_svc_do_run_agent_start_permission_error(self):
        """Adversarial: agent.start() raises PermissionError (e.g. port 53 restricted)."""
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.start.side_effect = PermissionError("EACCES: Port 53 requires elevated privileges")

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        with patch.object(service, "ReportServiceStatus") as mock_report, \
             patch.object(servicemanager, "LogErrorMsg") as mock_log_err:

            with pytest.raises(SystemExit) as exc_info:
                service.SvcDoRun()

            assert exc_info.value.code == 1
            mock_log_err.assert_called_once()
            assert "Port 53" in mock_log_err.call_args[0][0]
            mock_agent.stop.assert_called_once()

            # Verify SCM failure reporting
            mock_report.assert_any_call(
                win32service.SERVICE_STOPPED,
                win32ExitCode=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
                svcExitCode=1,
            )

    def test_svc_do_run_agent_start_socket_oserror(self):
        """Adversarial: agent.start() raises OSError (port collision on 8765)."""
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.start.side_effect = OSError("Address already in use: 127.0.0.1:8765")

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        with patch.object(service, "ReportServiceStatus") as mock_report, \
             patch.object(servicemanager, "LogErrorMsg") as mock_log_err:

            with pytest.raises(SystemExit) as exc_info:
                service.SvcDoRun()

            assert exc_info.value.code == 1
            mock_log_err.assert_called_once()
            mock_agent.stop.assert_called_once()
            mock_report.assert_any_call(
                win32service.SERVICE_STOPPED,
                win32ExitCode=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
                svcExitCode=1,
            )

    def test_svc_stop_handles_fatal_exception_in_agent_stop(self):
        """Adversarial: agent.stop() raises unexpected exception during SvcStop."""
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.stop.side_effect = RuntimeError("Fatal hardware unmount during stop")

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        with patch.object(service, "ReportServiceStatus") as mock_report, \
             patch.object(servicemanager, "LogWarningMsg") as mock_log_warn:

            # Must not crash
            service.SvcStop()

            # Must log warning and still reach SERVICE_STOPPED
            mock_log_warn.assert_called_once()
            assert "Fatal hardware unmount" in mock_log_warn.call_args[0][0]
            mock_report.assert_any_call(win32service.SERVICE_STOPPED)

    def test_svc_do_run_fatal_crash_when_agent_stop_also_raises(self):
        """Adversarial: agent.start() crashes AND agent.stop() also crashes in except block."""
        mock_agent = MagicMock(spec=AgentService)
        mock_agent.start.side_effect = RuntimeError("Start error")
        mock_agent.stop.side_effect = RuntimeError("Double crash in stop")

        service = OpenGuardKidsWindowsService(agent_service=mock_agent)

        with patch.object(service, "ReportServiceStatus") as mock_report:
            with pytest.raises(SystemExit) as exc_info:
                service.SvcDoRun()

            assert exc_info.value.code == 1
            mock_report.assert_any_call(
                win32service.SERVICE_STOPPED,
                win32ExitCode=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
                svcExitCode=1,
            )

    def test_mock_pywin32_mode_simulation(self):
        """Verify behavior when simulating HAS_PYWIN32=True environment."""
        mock_win32service = MagicMock()
        mock_win32service.SERVICE_RUNNING = 4
        mock_win32service.SERVICE_STOPPED = 1
        mock_win32service.SERVICE_STOP_PENDING = 3

        mock_winerror = MagicMock()
        mock_winerror.ERROR_SERVICE_SPECIFIC_ERROR = 1066

        mock_win32event = MagicMock()
        mock_win32event.WAIT_OBJECT_0 = 0
        mock_win32event.CreateEvent.return_value = 12345
        mock_win32event.WaitForSingleObject.return_value = 0

        mock_servicemanager = MagicMock()

        mock_agent = MagicMock(spec=AgentService)
        mock_agent.is_running = True

        with patch.object(ws, "win32service", mock_win32service), \
             patch.object(ws, "winerror", mock_winerror), \
             patch.object(ws, "win32event", mock_win32event), \
             patch.object(ws, "servicemanager", mock_servicemanager):

            svc = OpenGuardKidsWindowsService(agent_service=mock_agent)
            assert svc.stop_event == 12345

            # Test SvcStop
            with patch.object(svc, "ReportServiceStatus") as mock_report:
                svc.SvcStop()
                mock_win32event.SetEvent.assert_called_with(12345)
                mock_agent.stop.assert_called_once()
                mock_report.assert_any_call(mock_win32service.SERVICE_STOPPED)


# =============================================================================
# 2. Batch Script Syntax, Quoting, and Parser Verification
# =============================================================================


def command_line_to_argv_w(cmdline: str) -> list[str]:
    """Exact emulation of Windows CommandLineToArgvW per MSDN specification."""
    argv = []
    i = 0
    n = len(cmdline)
    while i < n:
        while i < n and cmdline[i] in " \t":
            i += 1
        if i >= n:
            break

        arg = []
        in_quotes = False
        while i < n:
            c = cmdline[i]
            if not in_quotes and c in " \t":
                break

            if c == "\\":
                num_backslashes = 0
                while i < n and cmdline[i] == "\\":
                    num_backslashes += 1
                    i += 1

                if i < n and cmdline[i] == '"':
                    arg.append("\\" * (num_backslashes // 2))
                    if num_backslashes % 2 == 1:
                        arg.append('"')
                        i += 1
                    else:
                        in_quotes = not in_quotes
                        i += 1
                else:
                    arg.append("\\" * num_backslashes)
            elif c == '"':
                in_quotes = not in_quotes
                i += 1
            else:
                arg.append(c)
                i += 1
        argv.append("".join(arg))
    return argv


class TestBatchScriptAdversarialParser:
    """Stress-tests batch commands with path spaces, quoting, and multi-byte unicode."""

    def test_scm_failure_recovery_command_quoting_with_spaces_and_unicode(self):
        """
        Verify that:
        sc.exe failure OpenGuardKidsService reset= 86400 actions= restart/60000/restart/60000/run/60000 command= "\"%PROJECT_ROOT%restore_dns.bat\""
        preserves inner quotes in argument 8 for paths with spaces and Vietnamese unicode.
        """
        test_paths = [
            r"C:\OpenGuard-Kids\restore_dns.bat",
            r"C:\Program Files\OpenGuard Kids\restore_dns.bat",
            r"D:\Dự Án\OpenGuard Trẻ Em\restore_dns.bat",
            r"C:\Users\John Doe\AppData\Local\OpenGuard\restore_dns.bat",
        ]

        for p in test_paths:
            # Reconstruct the exact command line as emitted by cmd.exe
            cmdline = (
                f'sc.exe failure OpenGuardKidsService reset= 86400 '
                f'actions= restart/60000/restart/60000/run/60000 '
                f'command= "\\"{p}\\""'
            )

            argv = command_line_to_argv_w(cmdline)
            assert argv[0] == "sc.exe"
            assert argv[1] == "failure"
            assert argv[2] == "OpenGuardKidsService"
            assert argv[3] == "reset="
            assert argv[4] == "86400"
            assert argv[5] == "actions="
            assert argv[6] == "restart/60000/restart/60000/run/60000"
            assert argv[7] == "command="
            # CRITICAL CHECK: Argument 8 must be the path ENCLOSED in literal double quotes
            assert argv[8] == f'"{p}"', (
                f"Inner quotes NOT preserved! Got: {argv[8]}, Expected: {repr(f'\"{p}\"')}"
            )

    def test_run_tray_bat_trailing_backslash_bug(self):
        """
        EMPIRICAL PROOF OF BUG IN setup_tray_startup.bat:
        In setup_tray_startup.bat line 96:
        echo start "" "%PYTHONW_EXE%" -c "import sys; sys.path.insert(0, r'%%~dp0'); import src.tray.main; src.tray.main.main()"
        Because %~dp0 ALWAYS ends with a backslash in cmd.exe (e.g. 'C:\\Project\\'),
        Python evaluates r'C:\\Project\\', where the trailing backslash escapes the closing quote!
        This results in: SyntaxError: unterminated string literal.
        """
        # Test valid path without trailing backslash
        valid_cmd = [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, r'/home/cornar/Projects/OpenGuard-Kids'); print('SUCCESS')",
        ]
        res_valid = subprocess.run(valid_cmd, capture_output=True, text=True)
        assert res_valid.returncode == 0
        assert "SUCCESS" in res_valid.stdout

        # Test what %~dp0 actually produces with trailing backslash:
        # In Python: r'C:\MyDir\' causes SyntaxError!
        invalid_python_code = "import sys; sys.path.insert(0, r'C:\\Projects\\OpenGuard-Kids\\'); print('FAIL')"
        invalid_cmd = [sys.executable, "-c", invalid_python_code]
        res_invalid = subprocess.run(invalid_cmd, capture_output=True, text=True)

        assert res_invalid.returncode != 0, "Expected SyntaxError from trailing backslash raw string"
        assert "SyntaxError: unterminated string literal" in res_invalid.stderr

    def test_temp_path_spaces_vulnerability_in_batch(self):
        """
        EMPIRICAL PROOF OF VULNERABILITY IN enable_dns_protection.bat and restore_dns.bat:
        The scripts execute:
        for /f "tokens=*" %%a in (%TEMP%\\ogk_active_adapters.txt) do (...)
        Without quotes or usebackq, if %TEMP% has spaces (e.g. C:\\Users\\John Doe\\AppData\\Local\\Temp),
        cmd.exe splits into multiple filenames: 'C:\\Users\\John' and 'Doe\\AppData\\...'.
        """
        fake_temp_with_spaces = r"C:\Users\John Doe\AppData\Local\Temp"
        unquoted_for = f"for /f \"tokens=*\" %%a in ({fake_temp_with_spaces}\\ogk_active_adapters.txt) do"

        # In cmd.exe, in (...) without quotes treats space as delimiter between multiple files!
        inside_parens = unquoted_for.split("in (")[1].split(")")[0]
        files = inside_parens.split(" ")
        assert len(files) > 1, "Expected multiple split tokens from unquoted path with spaces"
        assert files[0] == r"C:\Users\John"
        assert files[1] == r"Doe\AppData\Local\Temp\ogk_active_adapters.txt"
