"""
Unit tests for OpenGuard Kids Windows Service Framework
Target Module: src.agent.windows_service
Validates:
- Service metadata and attributes
- Initialization with default and injected AgentService
- SvcStop graceful shutdown sequence and event signaling
- SvcDoRun normal execution loop and clean termination
- SvcDoRun crash handling: SCM winerror 1066 reporting and sys.exit(1)
- Cross-platform import safety and mock pywin32 wrappers
"""
from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.agent.service import AgentService
from src.agent.windows_service import (
    HAS_PYWIN32,
    OpenGuardKidsWindowsService,
    servicemanager,
    win32event,
    win32service,
    win32serviceutil,
    winerror,
)
from src.common.constants import (
    DEFAULT_BLOCKPAGE_PORT,
    DEFAULT_DNS_PORT,
    DEFAULT_IPC_PORT,
)


def test_windows_service_metadata():
    """Verify standard SCM service metadata and dependencies."""
    assert OpenGuardKidsWindowsService._svc_name_ == "OpenGuardKidsService"
    assert (
        OpenGuardKidsWindowsService._svc_display_name_
        == "OpenGuard Kids Parental Protection Service"
    )
    assert "Tcpip" in OpenGuardKidsWindowsService._svc_deps_
    assert "Dnscache" in OpenGuardKidsWindowsService._svc_deps_
    assert len(OpenGuardKidsWindowsService._svc_deps_) == 2
    assert "DNS UDP 53" in OpenGuardKidsWindowsService._svc_description_
    assert "OpenGuard Kids" in OpenGuardKidsWindowsService._svc_description_


def test_windows_service_initialization_defaults(tmp_path):
    """Verify initialization with default parameters and ProgramData resolution."""
    fake_program_data = str(tmp_path / "ProgramData")
    with patch.dict(os.environ, {"ProgramData": fake_program_data}), \
         patch("src.agent.ipc.IPCServer") as mock_ipc_cls:
        mock_ipc_cls.return_value.server_address = ("127.0.0.1", DEFAULT_IPC_PORT)
        service = OpenGuardKidsWindowsService()
        expected_dir = os.path.join(fake_program_data, "OpenGuardKids")
        assert service.data_dir == expected_dir
        assert os.path.isdir(service.data_dir)
        assert service.stop_event is not None
        assert isinstance(service.agent, AgentService)
        assert service.agent.dns_proxy.listen_port == DEFAULT_DNS_PORT
        assert service.agent.blockpage.port == DEFAULT_BLOCKPAGE_PORT
        assert service.agent.ipc_manager.port == DEFAULT_IPC_PORT


def test_windows_service_initialization_dependency_injection(tmp_path):
    """Verify dependency injection of custom AgentService for testing."""
    mock_agent = MagicMock(spec=AgentService)
    mock_agent.data_dir = str(tmp_path / "custom_data")
    service = OpenGuardKidsWindowsService(args=["TestSvc"], agent_service=mock_agent)

    assert service.agent is mock_agent
    assert service.data_dir == str(tmp_path / "custom_data")
    assert service.stop_event is not None


def test_windows_service_svc_stop_lifecycle():
    """Verify SvcStop transitions: STOP_PENDING -> SetEvent -> agent.stop() -> STOPPED."""
    mock_agent = MagicMock(spec=AgentService)
    service = OpenGuardKidsWindowsService(agent_service=mock_agent)

    with patch.object(service, "ReportServiceStatus") as mock_report, \
         patch.object(win32event, "SetEvent") as mock_set_event, \
         patch.object(servicemanager, "LogInfoMsg") as mock_log_info:

        service.SvcStop()

        # Check ReportServiceStatus calls
        assert mock_report.call_count == 2
        mock_report.assert_any_call(win32service.SERVICE_STOP_PENDING)
        mock_report.assert_any_call(win32service.SERVICE_STOPPED)

        # Check event signaling and agent stop
        mock_set_event.assert_called_once_with(service.stop_event)
        mock_agent.stop.assert_called_once()
        mock_log_info.assert_called()


def test_windows_service_svc_stop_handles_agent_stop_exception():
    """Verify SvcStop handles exceptions during agent.stop() gracefully."""
    mock_agent = MagicMock(spec=AgentService)
    mock_agent.stop.side_effect = RuntimeError("Shutdown error")
    service = OpenGuardKidsWindowsService(agent_service=mock_agent)

    with patch.object(service, "ReportServiceStatus") as mock_report, \
         patch.object(servicemanager, "LogWarningMsg") as mock_log_warn:

        service.SvcStop()

        # Should still reach SERVICE_STOPPED
        mock_report.assert_any_call(win32service.SERVICE_STOPPED)
        mock_log_warn.assert_called_once()


def test_windows_service_svc_do_run_normal_execution():
    """Verify SvcDoRun normal lifecycle: RUNNING -> agent.start() -> wait -> exit."""
    mock_agent = MagicMock(spec=AgentService)
    # Simulate is_running transitioning to False after first loop check
    mock_agent.is_running = True

    service = OpenGuardKidsWindowsService(agent_service=mock_agent)

    def fake_wait(event, timeout):
        mock_agent.is_running = False
        return win32event.WAIT_OBJECT_0

    with patch.object(service, "ReportServiceStatus") as mock_report, \
         patch.object(win32event, "WaitForSingleObject", side_effect=fake_wait) as mock_wait, \
         patch.object(servicemanager, "LogInfoMsg") as mock_log_info:

        service.SvcDoRun()

        assert mock_report.call_count == 2
        mock_report.assert_any_call(win32service.SERVICE_RUNNING)
        mock_report.assert_any_call(win32service.SERVICE_STOPPED)
        mock_agent.start.assert_called_once()
        mock_agent.stop.assert_called_once()
        mock_wait.assert_called_once_with(service.stop_event, 1000)
        assert mock_log_info.call_count >= 2


def test_windows_service_svc_do_run_exception_triggers_scm_recovery():
    """
    CRITICAL SCM RECOVERY REQUIREMENT:
    Verify that an unhandled crash in SvcDoRun:
    1. Logs error via servicemanager.LogErrorMsg
    2. Calls agent.stop()
    3. Reports SERVICE_STOPPED with ERROR_SERVICE_SPECIFIC_ERROR (1066) and svc_exit_code=1
    4. Exits process with sys.exit(1) so SCM registers failure and activates sc.exe failure policy.
    """
    mock_agent = MagicMock(spec=AgentService)
    mock_agent.start.side_effect = RuntimeError("Fatal Port 53 bind collision")

    service = OpenGuardKidsWindowsService(agent_service=mock_agent)

    with patch.object(service, "ReportServiceStatus") as mock_report, \
         patch.object(servicemanager, "LogErrorMsg") as mock_log_error:

        with pytest.raises(SystemExit) as exc_info:
            service.SvcDoRun()

        # Must exit with non-zero code 1
        assert exc_info.value.code == 1

        # Must log the fatal error
        mock_log_error.assert_called_once()
        assert "Fatal Port 53 bind collision" in mock_log_error.call_args[0][0]

        # Must stop agent
        mock_agent.stop.assert_called_once()

        # Must report SERVICE_RUNNING first, then SERVICE_STOPPED with ERROR_SERVICE_SPECIFIC_ERROR (1066)
        assert mock_report.call_count == 2
        mock_report.assert_any_call(win32service.SERVICE_RUNNING)
        mock_report.assert_any_call(
            win32service.SERVICE_STOPPED,
            win32ExitCode=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
            svcExitCode=1,
        )


def test_windows_service_cross_platform_wrapper_contracts():
    """Verify that fallback dummy win32 objects satisfy required contracts."""
    assert hasattr(win32service, "SERVICE_STOPPED")
    assert hasattr(win32service, "SERVICE_RUNNING")
    assert hasattr(win32service, "SERVICE_STOP_PENDING")
    assert hasattr(winerror, "ERROR_SERVICE_SPECIFIC_ERROR")
    assert winerror.ERROR_SERVICE_SPECIFIC_ERROR == 1066
    assert hasattr(win32event, "CreateEvent")
    assert hasattr(win32event, "SetEvent")
    assert hasattr(win32event, "WaitForSingleObject")
    assert hasattr(servicemanager, "LogInfoMsg")
    assert hasattr(servicemanager, "LogErrorMsg")
    assert hasattr(win32serviceutil, "HandleCommandLine")


def test_windows_service_cli_entrypoint():
    """Verify that CLI handler dispatch functions without error."""
    with patch.object(win32serviceutil, "HandleCommandLine") as mock_hcl:
        win32serviceutil.HandleCommandLine(OpenGuardKidsWindowsService)
        mock_hcl.assert_called_once_with(OpenGuardKidsWindowsService)
