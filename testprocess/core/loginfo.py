from core.helpers.status import Status


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

    def get_last_log(self) -> list:
        """It returns the last meaningful log list.

        Returns
        -------
        list
            Last meaningful log list.
        """
        for per_result in reversed(self.result):
            if per_result:
                return per_result

    def get_status(self) -> int:
        """It checks if any status returned Status.ERROR.

        Returns
        -------
        int
            Status response of the command.
        """
        last_log = self.get_last_log()
        if last_log is not None:
            if f"'status': {Status.ERROR}" in last_log:
                return Status.ERROR
            elif f"'status': {Status.TIMEOUT}" in last_log:
                return Status.TIMEOUT
            elif f"'status': {Status.SUCCESS}" in last_log:
                return Status.SUCCESS
        return Status.UNKNOWN
