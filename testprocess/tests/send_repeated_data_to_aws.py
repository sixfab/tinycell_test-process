"""
This is a test file to test
sending repeated data into Amazon Web Services
with high frequencies.
"""
from core.testermanager import TesterManager, Step

TEST_NAME = "send_repeated_data_to_aws"
REPEAT_COUNT = 15  # The amount of message will be sent to AWS.


_FUNCTION_NAME = "modem.aws.publish_message"
_SEND_COUNT = 0


def get_different_data():
    """Creates payload with given parameter."""
    global _SEND_COUNT
    payload = '\'{"state": {"reported": {"SensorValue": '
    payload += str(_SEND_COUNT)
    payload += "}}}'"
    _SEND_COUNT += 1
    return payload


def step_factory(step_count: int, manager: TesterManager) -> None:
    """This function returns a list of steps
    that will be executed by the test."""
    step_names = [f"step_{str(index)}" for index in range(1, step_count + 1)]
    for step_index in range(step_count):
        # Next step is success or failure if it is last step.
        next_step_success = step_names[step_index + 1] if step_index < step_count - 1 else "success"
        next_step_failure = step_names[step_index + 1] if step_index < step_count - 1 else "failure"
        manager.add_step(
            Step(
                name=step_names[step_index],
                function=_FUNCTION_NAME,
                function_params={"payload": get_different_data()},
                success=next_step_success,
                fail=next_step_failure,
                retry=3,
            )
        )
    return manager


# Create zeroth step for the constructor parameter of manager.
step_zeroth = Step(
    name="step_0",
    function=_FUNCTION_NAME,
    success="step_1",
    fail="step_1",
    function_params={"payload": get_different_data()},
)

# Create state manager and append steps.
state_manager = TesterManager(step_zeroth, TEST_NAME)
state_manager.add_step(step_zeroth)
state_manager = step_factory(step_count=REPEAT_COUNT - 1, manager=state_manager)
