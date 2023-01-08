"""
This is a dummy test file to use
as development purposes.
"""
from core.testermanager import TesterManager, Step


def long_delay():
    import time

    time.sleep(300)


# Steps for the test
step_one_success = Step(
    name="step_one",
    function="modem.network.set_apn",
    success="step_two",
    fail="failure",
    function_params={"apn": "'super'"},
)

step_two_success = Step(
    name="step_two",
    function="modem.network.register_network",
    success="step_three",
    fail="failure"
)

step_three = Step(
    name="step_three",
    function="long_delay",
    success="success",
    fail="failure"
)


# Create state manager and append steps.
state_manager = TesterManager(step_one_success, "dummy_test")
state_manager.add_step(step_one_success)
state_manager.add_step(step_two_success)
state_manager.add_step(step_three)
