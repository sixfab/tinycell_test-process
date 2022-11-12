"""
Module for managing processes on modem step by step.
It is adapted from tinycell MicroPython SDK.
"""
import time

from helpers.cache import cache
from helpers.status import Status
from helpers.manager import StateManager, Step
from helpers.pyboard import Pyboard, PyboardError


class TesterManager(StateManager):
    """
    This class is an oriented implementation
    for the testing purposes which uses StateManager
    as its base class.
    """

    def __init__(self, first_step, function_name=None) -> None:
        # User-defined attributes.
        self.tinycell_port: str = None
        # Internal attributes.
        self.pyb: Pyboard = None
        self.logs: str = ""
        self.total_elapsed_time: float = 0.0

        # It sets the current step to the first one,
        # and get the base class attributes.
        super().__init__(first_step, function_name)

    def set_port(self, port: str) -> None:
        """It sets the port of the device."""
        self.tinycell_port = port
        self.pyb = Pyboard(self.tinycell_port)

    def run_the_test(self) -> str:
        """It runs all the steps on the
        state manager and returns the result.

        Returns
        -------
        str
            Logs of the test process.
        """
        self._start_repl()
        print("Starting the test process...")
        self._prepare_setup()
        result = self.run()
        print(result)
        self._stop_repl()

    ############################
    ##    INTERNAL METHODS    ##
    ############################
    def _start_repl(self) -> None:
        """It opens the REPL."""
        if self.pyb.in_raw_repl:
            raise PyboardError("The REPL is already open.")
        self.pyb.enter_raw_repl()

    def _stop_repl(self) -> None:
        """It closes the REPL."""
        if not self.pyb.in_raw_repl:
            raise PyboardError("The REPL is already closed.")
        self.pyb.exit_raw_repl()

    def _prepare_setup(self) -> None:
        """It prepares the ordinary setup."""
        commands_to_send = [
            "from core.modem import Modem;"
            "modem = Modem();"
        ]
        # Send each command.
        for command in commands_to_send:
            self.pyb.exec(command)

    def _send_command(self, command: str) -> dict:
        """
        It sends a command to the device.

        Returns:
        --------
        dict
            It includes the status, response and
            elapsed time of the command.
        """
        start_execution_time = time.time()
        self.pyb.exec_(f"result = {command}")
        elapsed_time = time.time() - start_execution_time
        result_string = self.pyb.exec_("print(result)")

        # Extract the dictionary from the result.
        result = self._extract_return(result_string)

        return {
            "status": result.get("status"),
            "response": result.get("response"),
            "elapsed_time": elapsed_time,
        }

    def _extract_return(self, result_string: str) -> dict:
        """
        It extracts the return value from the result string.

        Parameters
        ----------
        result_string : str
            String returned from the device.

        Returns
        -------
        dict
            Dictionary with the status, response and elapsed time.
        """
        pass

    ############################
    ##   OVERRIDEN METHODS    ##
    ############################
    def execute_current_step(self) -> dict:
        """
        This is an internal function to execute the current step.
        and capture elapsed time and logs.
        """
        params = self.current.function_params

        # Construct the command to be sent.
        if params:
            command = f"{self.current.function}("
            for key, value in params.items():
                command = command + f"{key}={value},"
            command = command[:-1] + ")"
            self.current.function = command

        # It sends the command to the device.
        result = self._send_command(self.current.function)

        # Update the cache and manager parameters.
        self.total_elapsed_time = self.total_elapsed_time + result.get("elapsed_time")
        cache.set_last_response(result.get("response"))
        if result.get("status") == Status.SUCCESS:
            self.current.is_ok = True
        else:
            self.current.is_ok = False

        return result
