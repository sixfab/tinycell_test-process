"""
This is a test file to test
sending GPS data into AWS.
"""
from core.testermanager import TesterManager, Step


TEST_NAME = "gps_tracker"
PERIOD_FIX = 2  # seconds

step_set_gnss = Step(
    name="modem_set_gnss",
    function="modem.gps.set_priority",
    success="gps_turn_on",
    fail="failure",
    function_params={"priority": 0},
)

step_gps_turn_on = Step(
    name="gps_turn_on",
    function="modem.gps.turn_on",
    success="gps_get_location",
    fail="failure",
)

step_get_location = Step(
    name="gps_get_location",
    function="modem.gps.get_location",
    success="modem_set_wwan",
    fail="failure",
    retry=45,
    interval=PERIOD_FIX,
)

step_set_wwan = Step(
    name="modem_set_wwan",
    function="modem.gps.set_priority",
    success="gps_turn_off",
    fail="failure",
    function_params={"priority": 1},
)

step_gps_turn_off = Step(
    name="gps_turn_off",
    function="modem.gps.turn_off",
    success="update_aws",
    fail="failure",
)

step_update_aws = Step(
    name="update_aws",
    function="modem.aws.publish_message",
    success="success",
    fail="failure",
    function_params={"payload": "'some_value'"},
)

state_manager = TesterManager(step_set_gnss, TEST_NAME)
state_manager.add_step(step_set_gnss)
state_manager.add_step(step_gps_turn_on)
state_manager.add_step(step_get_location)
state_manager.add_step(step_set_wwan)
state_manager.add_step(step_gps_turn_off)
state_manager.add_step(step_update_aws)
