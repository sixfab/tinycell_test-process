"""Module for config"""
import os
from dotenv import load_dotenv

# TEMP_PATH = os.path.expanduser("~") + "/.tinycell_test-coordinator"
TEMP_PATH = "."
ENVIRONMENT_PATH = f"{TEMP_PATH}/.env"
TESTS_DIR = "tests"

REPORT_PATH = f"{TEMP_PATH}/reports/"

if not os.path.exists(REPORT_PATH):
    os.makedirs(REPORT_PATH)

load_dotenv(ENVIRONMENT_PATH)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_REPORT_CHANNEL_ID = os.environ.get("SLACK_REPORT_CHANNEL_ID")
SLACK_COMMAND_CHANNEL = os.environ.get("SLACK_COMMAND_CHANNEL")
