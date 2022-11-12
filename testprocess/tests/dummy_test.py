"""
This is a dummy test file to use
as development purposes.
"""
from testermanager import TesterManager, Step

# Steps for the test
step_one_success = Step(
    name="step_one",
    function="modem.network.check_apn",
    success="step_two_success",
    fail="failure",
    function_params={"apn": "'super'"},
)

step_two_success = Step(
    name="step_two",
    function="modem.network.check_network_registration()",
    success="success",
    fail="failure"
)

# Create state manager and append steps.
state_manager = TesterManager(step_one_success, "dummy_test")
state_manager.add_step(step_one_success)
state_manager.add_step(step_two_success)
