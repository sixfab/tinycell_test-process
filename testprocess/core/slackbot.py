"""
This modules handles the connection and sending messages to Slack.
"""

import json
from slack_bolt import App


class SlackBot:
    """This class is used to send messages to slack."""

    def __init__(self, bot_token: str, channel_id: str) -> None:
        """This function initializes the SlackBot class."""
        self.app = App(token=bot_token)
        # Note that this is the channel ID but not its name.
        self.channel = channel_id

    def send_results(self, test_result: dict) -> None:
        """This function sends a message to the channel."""
        json_logs = json.dumps(test_result.get("logs"), indent=4)

        message: str = (
            f'==== Test Results for _{test_result.get("test_name")}_ ====\n'
            f'- Status: *{test_result.get("status_of_test")}*\n'
            f'- Device Port: {test_result.get("device_port")}\n'
            f'- Total Elapsed Time: {test_result.get("total_elapsed_time")}\n\n'
        )

        try:
            while True:
                result = self.app.client.files_upload_v2(
                    channel=self.channel,
                    initial_comment=message,
                    content=json_logs,
                    filename="test_results.json",
                )

                if result.get("ok"):
                    break

        # @TODO: Change the Exception type to SlackApiError.
        except Exception as error:
            print(f"Error: {error}")
