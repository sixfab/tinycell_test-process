"""
Module for managing processes on modem step by step.
It is adapted from tinycell MicroPython SDK.
"""
import os
import time
import json
from datetime import datetime

from core.helpers.status import Status
from core.helpers.manager import StateManager, Step
from core.helpers.pyboard import Pyboard, PyboardError


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
        for per_result in self.result:
            if f"'status': {Status.ERROR}" in per_result:
                return Status.ERROR

            if f"'status': {Status.TIMEOUT}" in per_result:
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
        self.test_started_on = (datetime.now()).strftime("%d_%m_%Y_%H_%M_%S")

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
        dict
            A dict which contains "logs" and "total_elapsed_time".
            Each logs is a dict which contains "command", "result"
            and "elapsed_time".
        """
        self._start_repl()
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

    def check_any_problem(self) -> int:
        """This method checks if there is any ERROR
        or TIMEOUT in the logs.

        Returns
        -------
        int
            A Status code.
        """
        for log in self.logs:
            if log.get_status() == Status.ERROR:
                return Status.ERROR

            if log.get_status() == Status.TIMEOUT:
                return Status.TIMEOUT

        return Status.SUCCESS

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

    def _add_log(self, command, result, elapsed_time) -> LogInfo:
        # Create log data.
        log = LogInfo(command, result, elapsed_time)
        # Add log to the list.
        self.logs.append(log)

        # Save the test information to a file.
        test_name = self.function_name
        test_port = self.tinycell_port.split("/")[-1]
        log_as_dict = log.to_dict()
        log_as_dict["test_name"] = test_name
        log_as_dict["test_port"] = test_port

        # Create the directory if it does not exist.
        file_location = f"./.logs/{test_port}-{test_name}-{self.test_started_on}.json"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "a", encoding="utf-8") as file:
            file.write(json.dumps(log_as_dict, indent=4) + ",\n")

        return log

    def _prepare_setup(self) -> None:
        """It prepares the ordinary setup.

        Returns:
        --------
        None
        """
        commands_to_send = [
            "from core.modem import Modem;",
            "from core.temp import debug;",
            "debug.set_level(0);",
            "modem = Modem();",
        ]

        # Send each command.
        for command in commands_to_send:
            starting_time = time.time()
            result_b = self.pyb.exec(command)
            elapsed_time = time.time() - starting_time

            # Append logs into logs list.
            result = self._extract_result(result_b)
            self._add_log(command, result, elapsed_time)

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
        result = self._extract_result(result_debug_b) + self._extract_result(
            result_command_b
        )
        # Add this command to logs.
        log = self._add_log(command, result, elapsed_time)

        return {
            "status": log.get_status(),
            "response": log.result,
            "elapsed_time": log.elapsed_time,
        }

    def _extract_result(self, result: bytearray) -> list:
        """It extracts the result from the bytearray.

        Parameters
        ----------
        result : bytearray
            The raw result of the command.

        Returns
        -------
        list
            The results of the command by item per line.
        """
        str_result = result.decode("utf-8")
        list_result = str_result.split("\r\n")
        list_result_no_empty = [item for item in list_result if item]
        return list_result_no_empty

    def _export_logs_as_dict(self) -> dict:
        """It returns the logs as a dict.

        Returns
        -------
        dict
            A dict which contains "logs" and "total_elapsed_time".
            Each logs is a dict which contains "command", "result"
            and "elapsed_time".
        """
        logs_as_dict_list = [log.to_dict() for log in self.logs]

        # Get status of test for more summarized information.
        status_of_test = "Status.SUCCESS"
        if self.check_any_problem() == Status.ERROR:
            status_of_test = "Status.ERROR"
        elif self.check_any_problem() == Status.TIMEOUT:
            status_of_test = "Status.TIMEOUT"

        return {
            "test_name": self.function_name,
            "device_port": self.tinycell_port,
            "total_elapsed_time": self.total_elapsed_time,
            "status_of_test": status_of_test,
            "logs": logs_as_dict_list,
        }

    ############################
    ##   OVERRIDEN METHODS    ##
    ############################
    def execute_current_step(self) -> dict:
        """
        This is an internal function to execute the current step.
        and capture elapsed time and logs.
        """
        # It is neccesary to check the name of the function,
        # because our implementation performs opeartions
        # on function call. And those does not have any call.
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
