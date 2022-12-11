"""
This is a test file to test
sending repeated data into Thingspeak
with high frequencies.
"""
from time import time
from core.testermanager import TesterManager, Step

TEST_NAME = "send_repeated_data_to_thingspeak"
REPEAT_COUNT = 150  # The amount of message will be sent to Thingspeak.


def get_different_data():
    """This function returns a different data
    each time it is called."""
    return {
        "field1": time(),
    }


def step_factory(step_count: int, manager: TesterManager) -> None:
    """This function returns a list of steps
    that will be executed by the test."""
    step_names = [f"step_{str(index)}" for index in range(1, step_count + 1)]
    for step_index in range(step_count):
        next_step = step_names[step_index + 1] if step_index < step_count - 1 else "success"
        manager.add_step(
            Step(
                name=step_names[step_index],
                function="modem.thingspeak.publish_message",
                function_params={"payload": get_different_data()},
                success=next_step,
                fail="failure",
            )
        )
    return manager


# Create zeroth step for the constructor parameter of manager.
step_zeroth = Step(
    name="step_zero",
    function="modem.thingspeak.publish_message",
    success="step_1",
    fail="failure",
    function_params={"payload": get_different_data()},
)

# Create state manager and append steps.
state_manager = TesterManager(step_zeroth, TEST_NAME)
state_manager = step_factory(step_count=REPEAT_COUNT - 1, manager=state_manager)
