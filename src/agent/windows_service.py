"""
OpenGuard Kids — Production Windows Service Framework
Target Platform: Windows 10/11 x64 (Session 0)
Module: src.agent.windows_service
Specification: docs/UPGRADE_PLAN.md Section 4.1 & ORIGINAL_REQUEST.md R1
"""
from __future__ import annotations

import logging
import os
import sys
import threading
from typing import Any, List, Optional

from src.agent.service import AgentService
from src.common.constants import (
    DEFAULT_BLOCKPAGE_PORT,
    DEFAULT_DNS_PORT,
    DEFAULT_IPC_PORT,
)

logger = logging.getLogger("OGK.WindowsService")

# -----------------------------------------------------------------------------
# Dual-Mode Platform Wrapper Pattern for pywin32
# Allows graceful execution and testing on Linux/CI without pywin32 installed.
# -----------------------------------------------------------------------------
try:
    import servicemanager
    import win32event
    import win32service
    import win32serviceutil
    import winerror

    HAS_PYWIN32 = True
    _BaseServiceFramework = win32serviceutil.ServiceFramework
except ImportError:
    HAS_PYWIN32 = False

    class _DummyWin32Service:
        SERVICE_STOPPED = 1
        SERVICE_START_PENDING = 2
        SERVICE_STOP_PENDING = 3
        SERVICE_RUNNING = 4
        SERVICE_CONTINUE_PENDING = 5
        SERVICE_PAUSE_PENDING = 6
        SERVICE_PAUSED = 7

    class _EventHandle:
        def __init__(self, initial_state: bool = False):
            self._event = threading.Event()
            if initial_state:
                self._event.set()

        def set(self):
            self._event.set()

        def clear(self):
            self._event.clear()

        def wait(self, timeout_sec: float | None = None) -> bool:
            return self._event.wait(timeout=timeout_sec)

        def is_set(self) -> bool:
            return self._event.is_set()

    class _DummyWin32Event:
        WAIT_OBJECT_0 = 0
        WAIT_TIMEOUT = 258
        WAIT_FAILED = -1

        @staticmethod
        def CreateEvent(security_attributes, manual_reset, initial_state, name):
            return _EventHandle(initial_state=bool(initial_state))

        @staticmethod
        def SetEvent(handle):
            if isinstance(handle, _EventHandle):
                handle.set()
            elif isinstance(handle, threading.Event):
                handle.set()
            return True

        @staticmethod
        def ResetEvent(handle):
            if isinstance(handle, _EventHandle):
                handle.clear()
            elif isinstance(handle, threading.Event):
                handle.clear()
            return True

        @staticmethod
        def WaitForSingleObject(handle, timeout_ms: int):
            timeout_sec = timeout_ms / 1000.0 if timeout_ms >= 0 else None
            signaled = False
            if isinstance(handle, _EventHandle):
                signaled = handle.wait(timeout_sec)
            elif isinstance(handle, threading.Event):
                signaled = handle.wait(timeout=timeout_sec)
            return _DummyWin32Event.WAIT_OBJECT_0 if signaled else _DummyWin32Event.WAIT_TIMEOUT

    class _DummyWinError:
        ERROR_SUCCESS = 0
        ERROR_SERVICE_SPECIFIC_ERROR = 1066
        ERROR_EXCEPTION_IN_SERVICE = 1064

    class _DummyServiceManager:
        @staticmethod
        def LogInfoMsg(msg: str):
            logger.info("[servicemanager.INFO] %s", msg)

        @staticmethod
        def LogWarningMsg(msg: str):
            logger.warning("[servicemanager.WARNING] %s", msg)

        @staticmethod
        def LogErrorMsg(msg: str):
            logger.error("[servicemanager.ERROR] %s", msg)

    class _DummyServiceFramework:
        def __init__(self, args: Optional[List[str]] = None):
            self.args = args or []
            self.status_history: List[dict[str, Any]] = []

        def ReportServiceStatus(
            self,
            status: int,
            win32ExitCode: int = 0,
            svcExitCode: int = 0,
            waitHint: int = 0,
            **kwargs: Any,
        ):
            # Capture both camelCase (pywin32 standard) and snake_case for backward compatibility
            w_exit = kwargs.get("win32_exit_code", win32ExitCode)
            s_exit = kwargs.get("svc_exit_code", svcExitCode)
            w_hint = kwargs.get("wait_hint", waitHint)
            checkpoint = kwargs.get("checkpoint", 0)
            record = {
                "status": status,
                "win32ExitCode": w_exit,
                "svcExitCode": s_exit,
                "waitHint": w_hint,
                "win32_exit_code": w_exit,
                "svc_exit_code": s_exit,
                "wait_hint": w_hint,
                "checkpoint": checkpoint,
            }
            self.status_history.append(record)

    class _DummyWin32ServiceUtil:
        ServiceFramework = _DummyServiceFramework

        @staticmethod
        def HandleCommandLine(cls: Any):
            logger.info("win32serviceutil.HandleCommandLine invoked for %s", cls)

    win32service = _DummyWin32Service()  # type: ignore
    win32event = _DummyWin32Event()  # type: ignore
    winerror = _DummyWinError()  # type: ignore
    servicemanager = _DummyServiceManager()  # type: ignore
    win32serviceutil = _DummyWin32ServiceUtil()  # type: ignore
    _BaseServiceFramework = _DummyServiceFramework


class OpenGuardKidsWindowsService(_BaseServiceFramework):
    """
    OpenGuard Kids native Windows NT Service running in Session 0.
    Under NT AUTHORITY\\LocalSystem, this service coordinates background protection:
    - DNS Proxy (UDP 53)
    - Polite Blockpage Server (HTTP 8080)
    - Screen Time Tracking & Idle Delegation
    - Process Whitelist/Blacklist Watcher
    - Offline Event SQLite WAL Buffer
    - Loopback IPC Channel (HTTP 8765)
    """

    _svc_name_ = "OpenGuardKidsService"
    _svc_display_name_ = "OpenGuard Kids Parental Protection Service"
    _svc_description_ = (
        "Dịch vụ nền bảo vệ trẻ em OpenGuard Kids: Quản lý thời gian sử dụng, "
        "lọc nội dung mạng DNS UDP 53, kiểm soát phần mềm vi phạm và đồng hành an toàn."
    )
    _svc_deps_ = ["Tcpip", "Dnscache"]

    def __init__(
        self,
        args: Optional[List[str]] = None,
        agent_service: Optional[AgentService] = None,
    ):
        super().__init__(args or [self._svc_name_])
        self._current_status: int = win32service.SERVICE_STOPPED
        if not hasattr(self, "status_history"):
            self.status_history = []
        # Stop signal event for SCM control
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        # Resolve system-wide ProgramData directory
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        self.data_dir = os.path.join(program_data, "OpenGuardKids")
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            logger.warning("Could not pre-create data_dir %s: %s", self.data_dir, e)

        # Support dependency injection for unit testing without port conflicts
        if agent_service is not None:
            self.agent = agent_service
            if hasattr(agent_service, "data_dir") and agent_service.data_dir:
                self.data_dir = agent_service.data_dir
        else:
            self.agent = AgentService(
                data_dir=self.data_dir,
                dns_port=DEFAULT_DNS_PORT,
                blockpage_port=DEFAULT_BLOCKPAGE_PORT,
                ipc_port=DEFAULT_IPC_PORT,
            )

    def ReportServiceStatus(
        self,
        status: int,
        win32ExitCode: int = 0,
        svcExitCode: int = 0,
        waitHint: int = 0,
        **kwargs: Any,
    ):
        """
        Reports service status to Windows SCM.
        Normalizes both camelCase (pywin32 standard) and snake_case kwargs,
        tracks active status in self._current_status, and forwards compliant
        camelCase arguments to the base ServiceFramework.
        """
        w_exit = kwargs.get("win32_exit_code", win32ExitCode)
        s_exit = kwargs.get("svc_exit_code", svcExitCode)
        w_hint = kwargs.get("wait_hint", waitHint)
        self._current_status = status

        if HAS_PYWIN32:
            super().ReportServiceStatus(
                status,
                waitHint=w_hint,
                win32ExitCode=w_exit,
                svcExitCode=s_exit,
            )
        else:
            super().ReportServiceStatus(
                status,
                win32ExitCode=w_exit,
                svcExitCode=s_exit,
                waitHint=w_hint,
                **kwargs,
            )

    def SvcStop(self):
        """
        SCM Stop handler.
        Transitions through SERVICE_STOP_PENDING, signals event, stops agent,
        and finally reports SERVICE_STOPPED.
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self._current_status = win32service.SERVICE_STOP_PENDING
        servicemanager.LogInfoMsg("OpenGuardKidsService is stopping...")
        win32event.SetEvent(self.stop_event)
        try:
            self.agent.stop()
        except Exception as e:
            servicemanager.LogWarningMsg(f"Error during agent shutdown: {e}")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        self._current_status = win32service.SERVICE_STOPPED

    def SvcDoRun(self):
        """
        SCM Main service execution loop running in Session 0.
        Transitions to SERVICE_RUNNING, starts agent orchestrator, and waits
        on self.stop_event. In case of fatal unhandled exception, notifies SCM
        with ERROR_SERVICE_SPECIFIC_ERROR and sys.exit(1) to trigger SCM recovery.
        On loop termination, cleanly stops agent and reports SERVICE_STOPPED.
        """
        servicemanager.LogInfoMsg("OpenGuardKidsService is starting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self._current_status = win32service.SERVICE_RUNNING
        agent_stopped = False

        try:
            self.agent.start()
            servicemanager.LogInfoMsg("OpenGuardKidsService started successfully.")
            while getattr(self.agent, "is_running", False):
                rc = win32event.WaitForSingleObject(self.stop_event, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
        except Exception as e:
            servicemanager.LogErrorMsg(
                f"OpenGuardKidsService encountered a fatal error: {e}"
            )
            try:
                self.agent.stop()
                agent_stopped = True
            except Exception:
                pass

            # Report ERROR_SERVICE_SPECIFIC_ERROR (1066) to Windows SCM using camelCase
            self.ReportServiceStatus(
                win32service.SERVICE_STOPPED,
                win32ExitCode=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
                svcExitCode=1,
            )
            self._current_status = win32service.SERVICE_STOPPED
            # Terminate with exit code 1 to ensure SCM registers failure
            sys.exit(1)
        finally:
            # Ensure agent is stopped cleanly if not already stopped in except handler
            if not agent_stopped:
                try:
                    self.agent.stop()
                except Exception as e:
                    servicemanager.LogWarningMsg(f"Error during agent shutdown: {e}")

            # Report SERVICE_STOPPED if not already reported as stopped
            if getattr(self, "_current_status", None) != win32service.SERVICE_STOPPED:
                self.ReportServiceStatus(win32service.SERVICE_STOPPED)
                self._current_status = win32service.SERVICE_STOPPED


if __name__ == "__main__":
    if HAS_PYWIN32:
        win32serviceutil.HandleCommandLine(OpenGuardKidsWindowsService)
    else:
        print("pywin32 is not installed. Windows Service requires pywin32 on Windows.")
