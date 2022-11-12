"""
Module for managing processes on modem step by step.
It is adapted from tinycell MicroPython SDK.
"""
import time

from helpers.status import Status
from helpers.manager import StateManager, Step
from helpers.pyboard import Pyboard, PyboardError


class LogInfo:
    """This class stores the log information of the command."""

    def __init__(self, command, result, elapsed_time) -> None:
        self.result = result
        self.elapsed_time = elapsed_time
        self.command = command

    def to_dict(self) -> dict:
        """It returns the log as dict."""
        return {
            "command": self.command,
            "result": self.result,
            "elapsed_time": self.elapsed_time,
        }

    def get_status(self) -> bool:
        """It checks if any status returned Status.ERROR.

        Returns
        -------
        bool
            True if command succees, False otherwise.
        """
        if f"'status': {Status.ERROR}" in self.result:
            return Status.ERROR

        if f"'status': {Status.TIMEOUT}" in self.result:
            return Status.TIMEOUT

        return Status.SUCCESS


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
        self.logs: list = []
        self.total_elapsed_time: float = 0.0

        # It sets the current step to the first one,
        # and get the base class attributes.
        super().__init__(first_step, function_name)

    def set_port(self, port: str) -> None:
        """It sets the port of the device."""
        self.tinycell_port = port
        self.pyb = Pyboard(self.tinycell_port)

    def run_the_test(self) -> list:
        """It runs all the steps on the
        state manager and returns the result.

        Returns
        -------
        [logs, total_elapsed_time] : list
            It returns the logs and the total elapsed time.
        """
        self._start_repl()
        print("Starting the test process...")
        # Send the setup commands.
        self._prepare_setup()

        # Run the state manager.
        while True:
            result = self.run()
            if result["status"] != Status.ONGOING:
                break
            time.sleep(result["interval"])

        # Close the REPL.
        self._stop_repl()

        # Return the logs.
        return self._export_logs_as_dict()

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
            "from core.modem import Modem;",
            "from core.temp import debug;",
            "debug.set_level(0);",
            "modem = Modem();",
        ]

        # Send each command.
        for command in commands_to_send:
            starting_time = time.time()
            log_b = self.pyb.exec(command)
            elapsed_time = time.time() - starting_time

            # Append logs into logs list.
            log = LogInfo(command, log_b.decode("utf-8"), elapsed_time)
            self.logs.append(log)

            # Increase total elipsed time.
            self.total_elapsed_time += elapsed_time

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
        result_debug_b = self.pyb.exec_(f"result = {command}")
        elapsed_time = time.time() - start_execution_time
        result_command_b = self.pyb.exec_("print(result)")

        # Extract information from the byte array.
        result = self._extract_return(result_debug_b, result_command_b)
        # Add this command to logs.
        log = LogInfo(command, result, elapsed_time)
        self.logs.append(log)

        return {
            "status": log.get_status(),
            "response": log.result,
            "elapsed_time": log.elapsed_time,
        }

    def _extract_return(self, result_dbg: bytearray, result_cmd: bytearray) -> str:
        """
        It extracts the return value from the result string.

        Parameters
        ----------
        result_dbg : bytearray
            Bytearray returned by the debug.
        result_cmd : bytearray
            Bytearray returned by the command.

        Returns
        -------
        str
            Combination of the debug and command result.
        """
        str_debug = result_dbg.decode("utf-8")
        str_command = result_cmd.decode("utf-8")
        return str_debug + str_command

    def _export_logs_as_dict(self) -> dict:
        """It returns the logs as a dict.

        Returns
        -------
        dict
            A dict which contains "logs" and "total_elapsed_time".
            Each logs is a dict which contains "command", "result"
            and "elapsed_time".
        """
        return {
            "total_elapsed_time": self.total_elapsed_time,
            "logs": [log.to_dict() for log in self.logs]
        }

    ############################
    ##   OVERRIDEN METHODS    ##
    ############################
    def execute_current_step(self) -> dict:
        """
        This is an internal function to execute the current step.
        and capture elapsed time and logs.
        """
        if self.current.name == "success":
            return {"status": Status.SUCCESS, "response": "Test has completed."}
        if self.current.name == "failure":
            return {"status": Status.ERROR, "response": "Test has failed."}

        params = self.current.function_params

        # Construct the command to be sent.
        self.current.function += "("
        if params:
            for key, value in params.items():
                self.current.function += f"{key}={value},"
            self.current.function = self.current.function[:-1]
        self.current.function += ")"

        # It sends the command to the device.
        result = self._send_command(self.current.function)

        # Update the cache and manager parameters.
        self.total_elapsed_time = self.total_elapsed_time + result.get("elapsed_time")
        if result.get("status") == Status.SUCCESS:
            self.current.is_ok = True
        else:
            self.current.is_ok = False

        return result
