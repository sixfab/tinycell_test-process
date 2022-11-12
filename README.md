# tinycell_test-process
Repo for testing tinycell devices over a linux OS. This program opens a serial connection between your host machine and Tinycell, and sends commmands using state manager architecture.

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

## TODO
- [X] Add support for function parameters given as step attribute.