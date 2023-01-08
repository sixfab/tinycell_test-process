"""
This is a dummy test file to use
as development purposes.
"""
import time
from core.testermanager import TesterManager, Step


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
    success="success",
    fail="failure"
)


# Create state manager and append steps.
state_manager = TesterManager(step_one_success, "dummy_test")
state_manager.add_step(step_one_success)
state_manager.add_step(step_two_success)

time.sleep(300)
