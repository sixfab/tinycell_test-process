"""
This is the main run file to execute
tests via given flag settings.
"""
import os
import argparse
import json
from importlib import import_module
from dotenv import load_dotenv

from core.helpers.config import SLACK_BOT_TOKEN, SLACK_REPORT_CHANNEL, TESTS_DIR
from core.slackbot import SlackBot


def init_argument_parser():
    """This function handles the flagging system with argparser.

    Returns
    -------
    Namespace
        Includes flags of the program.
    """
    parser = argparse.ArgumentParser(
        description="This program opens a serial connection between your"
        "host machine and Tinycell and sends commmands using"
        "state manager architecture."
    )
    parser.add_argument(
        "-p",
        "--port",
        nargs="+",
        required=True,
        help="Provide the port connected to Tinycell device.",
    )
    parser.add_argument(
        "-t",
        "--test",
        nargs="+",
        required=True,
        help="Provide the test file name in tests/ subdirectory.",
    )
    parser.add_argument(
        "-w",
        "--watchdog",
        nargs="+",
        required=False,
        help="Provide the timeout in seconds (per step) for Watchdog.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = init_argument_parser()

    # Check test files and ports.
    test_file_name: str = args.test[0]
    port_to_be_tested: str = args.port[0]
    watchdog_timeout: int = None
    if args.watchdog:
        watchdog_timeout = int(args.watchdog[0])

    # Import the given test file.
    test_sm = import_module(f"{TESTS_DIR}.{test_file_name}").state_manager

    # Create a process instance and run it.
    test_sm.set_port(port_to_be_tested)
    test_result = test_sm.run_the_test(watchdog_timeout)

    # Convert the result dict to JSON,
    # and print it.
    test_result_json = json.dumps(test_result)

    # Send the result to Slack.
    load_dotenv()

    slack_bot = SlackBot(SLACK_BOT_TOKEN, SLACK_REPORT_CHANNEL)
    slack_bot.send_results(test_result)
