"""
This modules handles the connection and sending messages to Slack.
"""

import json
from slack_bolt import App

class SlackBot:
    """This class is used to send messages to slack."""

    def __init__(self, bot_token: str, channel: str) -> None:
        """This function initializes the SlackBot class."""
        self.app = App(token=bot_token)
        self.channel = channel

    def send_results(self, test_result: dict) -> None:
        """This function sends a message to the channel."""
        json_logs = json.dumps(test_result.get("logs"), indent=4)

        message: str = (
            f'==== Test Results for _{test_result.get("test_name")}_ ====\n'
            f'- Status: *{test_result.get("status_of_test")}*\n'
            f'- Device Port: {test_result.get("device_port")}\n'
            f'- Total Elapsed Time: {test_result.get("total_elapsed_time")}\n\n'
            f"```\n"
            f"{json_logs}\n"
            f"```\n"
        )
        try:
            while True:
                result = self.app.client.chat_postMessage(
                    channel=self.channel, text=message
                )

                if result.get("ok"):
                    break

        # @TODO: Change the Exception type to SlackApiError.
        except Exception as error:
            print(f"Error: {error}")
