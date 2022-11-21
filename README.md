# tinycell_test-process
Repo for testing tinycell devices over a linux OS. This program opens a serial connection between your host machine and Tinycell, and sends commmands using state manager architecture. It does not output anything to standart output, but logs the current test results on `.log/` and sends a message to given Slack channel.

Example Slack message can be found below:
```md
==== Test Results for _test-name_ ====
- Status: Status.SUCCESS
- Device Port: /dev/ttyACM0
- Total Elapsed Time: 4.041985750198364
"""
[
    {
        "command": "SOME_COMMAND",
        "result": [],
        "elapsed_time": 3.1457700729370117
    },
    {
        "command": "SOME_OTHER_COMMAND",
        "result": [
           "SOME_DEBUG_MESSAGE",
           "SOME_DEBUG_MESSAGE",
           "SOME_DEBUG_MESSAGE",
        ],
        "elapsed_time": 0.43717122077941895
    },
    (...)
]
"""
```


## Usage
Before calling the `run.py`, make sure that you've installed modules in `requirements.txt` file.
```bash
~$ python run.py [-h] -p PORT [PORT ...] -t TEST [TEST ...]
```
### Status Types
These status messages will be returned by the program to Slack channel.
- `Status.SUCCESS`: All tests passed.
- `Status.ERROR`: At least one test failed.
- `Status.TIMEOUT`: At least one test timed out.
- `WATCHDOG_TIMEOUT`: Watchdog stopped the program.
- `TERMINATE_REQUEST`: Program was terminated by coordinator (SIGUSR1).

### Environmental Variables
You have to set three environmental variables to work with Slack.
- `SLACK_TOKEN`: Slack token for your bot.
- `SLACK_SIGNING_SECRET`: Slack signing secret for your bot.
- `SLACK_CHANNEL_ID`: Slack channel where you want to send the logs.

## Architecture
The architecture relies on a test manager class inherited from the state manager used in Tinycell SDK. The problem we did overcome is the implementation of `execute_current_step()` method which was calling a pointer with function parameters given. The inheritence allows us to re-implement that method with desired execution function. In TesterManager class, we send the given functions and their parameters into Tinycell device with using Pyboard tool.

The users has to create their test states with using TesterManager class.

### Hard-Stop for the Test
If you want to stop the test, you can send a `SIGUSR1` signal to the program. This will terminate the program and send a `TERMINATE_REQUEST` message to Slack channel.

## Creating Tests
Each test scenario is a state manager which has steps for each function should be called one-by-one. To create steps and state manager, you should import `testermanager.py` file which we have created. One can look the `dummy_test.py` file for an example.

**Note:** You need to put additional double quotes or single quotes for each string parameter in the function params attribute. For example, if you want to call `set_time()` function with `time="2020-01-01 00:00:00"` parameter, you should write it as `function_params="{'time': '"2020-01-01 00:00:00"'}"` in its step declearation.

## Logging
The script creates a log file for each runtime, and updates it with each step. Within this feature, you can obsorve the test results and the errors if any in case of empty or error-ed stdout. This log file can be found on the `.logs` folder.