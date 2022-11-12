"""
Data class for status.
"""


class Status:
    """To have a meaning for the status of the step."""

    SUCCESS = 0
    ERROR = 1
    TIMEOUT = 2
    ONGOING = 3
    UNKNOWN = 99
