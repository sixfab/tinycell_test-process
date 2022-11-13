# tinycell_test-process
Repo for testing tinycell devices over a linux OS. This program opens a serial connection between your host machine and Tinycell, and sends commmands using state manager architecture.

It outputs a JSON which has the following format:

```json
{
   "total_elapsed_time":5.1807169914245605,
   "logs":[
      {
         "command":"SOME_COMMAND",
         "result":[
            "SOME_RESULT_1",
            "SOME_RESULT_2",
            "SOME_RESULT_3",
         ],
         "elapsed_time":4.273318290710449
      },
      // (...)
   ]
}
```

## Usage
Before calling the `run.py`, make sure that you've installed modules in `requirements.txt` file.
```bash
~$ python run.py [-h] -p PORT [PORT ...] -t TEST [TEST ...]
```

## Architecture
The architecture relies on a test manager class inherited from the state manager used in Tinycell SDK. The problem we did overcome is the implementation of `execute_current_step()` method which was calling a pointer with function parameters given. The inheritence allows us to re-implement that method with desired execution function. In TesterManager class, we send the given functions and their parameters into Tinycell device with using Pyboard tool.

The users has to create their test states with using TesterManager class.

## Creating Tests
Each test scenario is a state manager which has steps for each function should be called one-by-one. To create steps and state manager, you should import `testermanager.py` file which we have created. One can look the `dummy_test.py` file for an example.

**Note:** You need to put additional double quotes or single quotes for each string parameter in the function params attribute. For example, if you want to call `set_time()` function with `time="2020-01-01 00:00:00"` parameter, you should write it as `function_params="{'time': '"2020-01-01 00:00:00"'}"` in its step declearation.

## Logging
The script creates a log file for each runtime, and updates it with each step. Within this feature, you can obsorve the test results and the errors if any in case of empty or error-ed stdout. This log file can be found on the `.logs` folder.