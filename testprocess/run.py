"""
This is the main run file to execute
tests via given flag settings.
"""
import argparse
from importlib import import_module


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

    return parser.parse_args()


if __name__ == "__main__":
    args = init_argument_parser()

    # Check test files and ports.
    test_file_name = args.test[0]
    port_to_be_tested = args.port[0]

    # Import the given test file.
    TESTS_DIR = "tests"
    test_sm = import_module(f"{TESTS_DIR}.{test_file_name}").state_manager

    # Create a process instance and run it.
    test_sm.set_port(port_to_be_tested)
    test_sm.run_the_test()
