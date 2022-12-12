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

    def get_status(self) -> int:
        """It checks if any status returned Status.ERROR.

        Returns
        -------
        int
            Status response of the command.
        """
        for per_result in self.result:
            if f"'status': {Status.ERROR}" in per_result:
                return Status.ERROR

            if f"'status': {Status.TIMEOUT}" in per_result:
                return Status.TIMEOUT

        return Status.SUCCESS
