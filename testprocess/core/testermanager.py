"""
Module for managing processes on modem step by step.
It is adapted from tinycell MicroPython SDK.
"""
import os
import sys
import time
import json
import signal
import logging
from datetime import datetime

from core.helpers.config import REPORT_PATH
from core.helpers.status import Status
from core.helpers.manager import StateManager, Step
from core.helpers.pyboard import Pyboard, PyboardError
from core.loginfo import LogInfo
from core.watchdog import Watchdog, WatchdogTimeout


class TerminateRequest(Exception):
    """This exception is raised when the test process is terminated."""

    def __init__(self, message: str) -> None:
        message: str = f"Terminate request: {message}"
        super().__init__(message)


class TesterManager(StateManager):
    """
    This class is an oriented implementation
    for the testing purposes which uses StateManager
    as its base class.
    """

    TERMINATION_SIGNAL = signal.SIGTERM

    # Settings of the logger
    debug_logger = logging.getLogger()
    debug_logger.setLevel(logging.DEBUG)

    debug_handler = logging.StreamHandler(sys.stdout)
    debug_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s --> %(levelname)-8s %(message)s")
    debug_handler.setFormatter(formatter)

    def __init__(self, first_step, function_name=None) -> None:
        # User-defined attributes.
        self.tinycell_port: str = None
        # Internal attributes.
        self.pyb: Pyboard = None
        self.watchdog: Watchdog = None
        self.wdg_timeout: int = 0

        self.logs: list = []
        self.total_elapsed_time: float = 0.0
        self.test_started_on: str = (datetime.now()).strftime("%d_%m_%Y_%H_%M_%S")

        # It sets the current step to the first one,
        # and get the base class attributes.
        super().__init__(first_step, function_name)

    def set_debugging(self, debug: bool) -> None:
        """It sets the debugging mode."""
        if debug:
            self.debug_logger.addHandler(self.debug_handler)
        else:
            self.debug_logger.removeHandler(self.debug_handler)

    def set_port(self, port: str) -> None:
        """It sets the port of the device."""
        self.tinycell_port = port
        self.pyb = Pyboard(self.tinycell_port)
        self.debug_logger.info("Port is set to %s.", self.tinycell_port)

    def run_the_test(self, timeout: int = None) -> list:
        """It runs all the steps on the
        state manager and returns the result.

        Parameters
        ----------
        timeout : int, optional
            Timeout for the watchdog, by default 5 minutes

        Returns
        -------
        dict
            A dict which contains "logs" and "total_elapsed_time".
            Each logs is a dict which contains "command", "result"
            and "elapsed_time".
        """
        # Set up the Watchdog.
        if timeout is None:
            timeout = 300  # seconds
        self.wdg_timeout = timeout
        self.watchdog = Watchdog(timeout, self._watchdog_handler)
        self.debug_logger.info("Watchdog is set to %d seconds.", timeout)

        # Append SIGTERM handler.
        signal.signal(self.TERMINATION_SIGNAL, self._sudden_kill_handler)

        try:
            self._start_repl()
            # Send the setup commands.
            self._prepare_setup()
            self.debug_logger.info("REPL started and setup commands are sent.")

            # Run the state manager.
            while True:
                # Run the current step.
                self.debug_logger.info("Running step %s.", self.current.name)
                result = self.run()
                self.debug_logger.info("Step %s is finished.", self.current.name)
                if result["status"] != Status.ONGOING:
                    break
                time.sleep(result["interval"])

            # Close the REPL.
            self._stop_repl()
            self.debug_logger.info("REPL is closed.")

        # If WatchdogTimeout is raised, append the status and finish test.
        except WatchdogTimeout:
            self.debug_logger.info("Watchdog timeout is raised.")
            self._add_log("WATCHDOG_TIMEOUT", "WATCHDOG_TIMEOUT", -1)
            logs_as_dict = self._export_logs_as_dict()
            logs_as_dict["status_of_test"] = "WATCHDOG_TIMEOUT"
            return logs_as_dict

        # If TerminateRequest came from coordinator, append the status and finish test.
        except TerminateRequest:
            self.debug_logger.info("Terminate request is raised.")
            self._add_log("TERMINATE_REQUEST", "TERMINATE_REQUEST", -1)
            logs_as_dict = self._export_logs_as_dict()
            logs_as_dict["status_of_test"] = "TERMINATE_REQUEST"
            return logs_as_dict

        except Exception as error_message:
            self.debug_logger.info("MicroPython exception is raised: \n%s", error_message)
            self._add_log("MicroPython Exception", str(error_message), -1)
            logs_as_dict = self._export_logs_as_dict()
            logs_as_dict["status_of_test"] = "MP_EXCEPTION"
            return logs_as_dict

        # Return the logs.
        self.debug_logger.info("Test is finished. Exporting logs.")
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

    def get_status_string(self) -> str:
        """It returns the last status of the logs.

        Returns
        -------
        string
            A Status indicator string.
        """
        # Get status of test for more summarized information.
        status_of_test = "Status.SUCCESS"
        if self.logs[-1].get_status() == Status.ERROR:
            status_of_test = "Status.ERROR"
        elif self.logs[-1].get_status() == Status.TIMEOUT:
            status_of_test = "Status.TIMEOUT"

        return status_of_test

    def get_status_string(self) -> str:
        """It returns the last status of the logs.

        Returns
        -------
        string
            A Status indicator string.
        """
        # Get status of test for more summarized information.
        status_of_test = "Status.SUCCESS"
        if self.logs[-1].get_status() == Status.ERROR:
            status_of_test = "Status.ERROR"
        elif self.logs[-1].get_status() == Status.TIMEOUT:
            status_of_test = "Status.TIMEOUT"

        return status_of_test

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
        file_location = f"{REPORT_PATH}/{test_port}-{test_name}-{self.test_started_on}.json"
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
        self.debug_logger.info("Sending command: %s.", command)
        start_execution_time = time.time()
        result_debug_b = self.pyb.exec_(f"result = {command}")
        elapsed_time = time.time() - start_execution_time
        result_command_b = self.pyb.exec_("print(result)")
        self.debug_logger.info(
            "Command is resulted as \t%s.", result_command_b.decode("utf-8")[:-2]
        )

        # Extract information from the byte array.
        result = self._extract_result(result_debug_b) + self._extract_result(result_command_b)
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

        return {
            "test_name": self.function_name,
            "device_port": self.tinycell_port,
            "total_elapsed_time": self.total_elapsed_time,
            "status_of_test": self.get_status_string(),
            "status_counts": self._get_status_counts(),
            "logs": logs_as_dict_list,
        }

    def _get_status_counts(self) -> dict:
        """It returns the number of each status type.

        Returns
        -------
        dict
            A dict which contains the status counts.
        """
        status_counts = {
            "Status.SUCCESS": 0,
            "Status.ERROR": 0,
            "Status.TIMEOUT": 0,
        }

        for log in self.logs:
            if log.get_status() == Status.SUCCESS:
                status_counts["Status.SUCCESS"] += 1
            elif log.get_status() == Status.ERROR:
                status_counts["Status.ERROR"] += 1
            elif log.get_status() == Status.TIMEOUT:
                status_counts["Status.TIMEOUT"] += 1
            elif log.get_status() == Status.UNKNOWN:
                pass
            else:
                raise ValueError("Couldn't parse status.")

        return status_counts

    def _watchdog_handler(self, signum: int, _):
        """It handles the watchdog timeout."""
        if signum == signal.SIGALRM:
            self._stop_repl()
            raise WatchdogTimeout(self._timeout_error_message())

    def _sudden_kill_handler(self, signum: int, _):
        """
        It handles the SIGTERM signal which
        comes from coordinator.
        """
        if signum == self.TERMINATION_SIGNAL:
            self._stop_repl()
            raise TerminateRequest("The test was terminated by the coordinator.")

    def _timeout_error_message(self):
        return (
            f"The test {self.function_name} has been interrupted "
            f"because it took more than {self.wdg_timeout} seconds."
        )

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

        # It checks if the current step is a retry
        if not "(" in self.current.function:
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

        # Kicks the Watchdog.
        self.watchdog.reset()

        return result
