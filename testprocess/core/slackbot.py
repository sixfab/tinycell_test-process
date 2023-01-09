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

    def send_text_message(self, message: str) -> None:
        """This function sends a text message to the channel."""
        return self.app.client.chat_postMessage(channel=self.channel, text=message)

    def send_results(self, test_result: dict) -> None:
        """This function sends a message to the channel."""
        json_logs = json.dumps(test_result.get("logs"), indent=4)

        message: str = (
            f'- *Test Script*: {test_result.get("test_name")}\n'
            f'- *Test Status*: {test_result.get("status_of_test")}\n'
            f'\t\t- Success: {test_result.get("status_counts").get("Status.SUCCESS")}\n'
            f'\t\t- Error: {test_result.get("status_counts").get("Status.ERROR")}\n'
            f'\t\t- Timeout: {test_result.get("status_counts").get("Status.TIMEOUT")}\n'
            f'- *Device Port*: {test_result.get("device_port")}\n'
            f'- *Total Elapsed Time*: {test_result.get("total_elapsed_time")}\n\n'
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
