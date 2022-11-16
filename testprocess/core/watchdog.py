"""
This module contains a software-defined Watchdog
timer to prevent the program from hanging.
"""

from signal import signal, alarm, SIGALRM
from typing import Callable


class WatchdogTimeout(Exception):
    """
    This exception is raised when the watchdog
    timer is triggered.
    """

    def __init__(self, message: str) -> None:
        message: str = f"Timeout reached: {message}"
        super().__init__(message)


class Watchdog:
    """
    This class is a watchdog to keep track of the
    test process. It is used to kill the test process.
    """

    def __init__(self, timeout: int, handler: Callable = None) -> None:
        self.timeout: int = timeout
        self.handler: Callable = handler or self._default_handler
        # Assign given handler to SIGALRM signal.
        signal(SIGALRM, self.handler)
        self.reset()

    def reset(self) -> None:
        """It kicks the Watchdog."""
        alarm(self.timeout)

    def _default_handler(self, signum: int, _) -> None:
        if signum == signal.SIGALRM:
            raise WatchdogTimeout("SIGALRM recieved.")
