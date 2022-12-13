"""
This is a test file which sends HTTP different requests to demo servers
with using different content types."""
from core.testermanager import TesterManager, Step

TEST_NAME = "http_send_requests"
# Will send PUT and GET to the first server.
# Will send POST and PUT requests to the second server.
SERVER_URL_1 = "https://webhook.site/691792ea-0abe-4dab-94a6-6d5bb49c4eec"
SERVER_URL_2 = "https://webhook.site/e858b02f-8521-4c7a-aba8-bde75a46bbfb"

def get_host_and_query(url: str, what_to_get: str = "host"):
    """Get host and query from the URL."""
    url = url.replace("https://", "").replace("http://", "")
    index = url.find("/") if url.find("/") != -1 else len(url)
    if what_to_get == "host":
        return url[:index]
    return url[index:]

def construct_get_header(url: str):
    """Construct custom header."""
    header = f"GET {get_host_and_query(url, 'query')} HTTP/1.1\\r"
    header += f"Host: {get_host_and_query(url, 'host')}\\r\\r"
    return header

# Steps to handle cellular network registration.
step_network_reg = Step(
    function="modem.network.register_network",
    name="register_network",
    success="get_pdp_ready",
    fail="failure",
    retry=3,
    interval=1,
)

step_pdp_ready = Step(
    function="modem.network.get_pdp_ready",
    name="get_pdp_ready",
    success="set_context_id",
    fail="failure",
    cachable=True,
)

step_set_context = Step(
    function="modem.http.set_context_id",
    name="set_context_id",
    success="set_server_url_one",
    fail="failure",
)

# Steps to send a JSON POST request to server one.
step_set_server_url_1 = Step(
    function="modem.http.set_server_url",
    name="set_server_url_one",
    success="set_content_type_one",
    fail="failure",
    function_params={"url": f"'{SERVER_URL_1}'"},
)

step_set_content_type_1 = Step(
    function="modem.http.set_content_type",
    name="set_content_type_one",
    success="send_json_post_request_to_first",
    fail="failure",
    function_params={"content_type": 4},
)

step_send_json_post_request_to_first = Step(
    function="modem.http.put",
    name="send_json_post_request_to_first",
    success="read_response_zeroth",
    fail="failure",
    function_params={"data": '\'{"test": "test"}\''},
)

step_read_response_zeroth = Step(
    function="modem.http.read_response",
    name="read_response_zeroth",
    success="set_server_url_two_for_json_post",
    fail="failure",
)

# Steps to send a JSON POST request to server two.
step_set_server_url_2 = Step(
    function="modem.http.set_server_url",
    name="set_server_url_two_for_json_post",
    success="send_json_post_request_to_second",
    fail="failure",
    function_params={"url": f"'{SERVER_URL_2}'"},
)

step_send_json_post_request_to_second = Step(
    function="modem.http.post",
    name="send_json_post_request_to_second",
    success="read_response_first",
    fail="failure",
    function_params={"data": '\'{"test": "test"}\''},
)

step_read_response_first = Step(
    function="modem.http.read_response",
    name="read_response_first",
    success="set_content_type_two",
    fail="failure",
)

# Steps to send a image/jpeg PUT request to server two.
step_set_content_type_2 = Step(
    function="modem.http.set_content_type",
    name="set_content_type_two",
    success="send_jpeg_put_request_to_second",
    fail="failure",
    function_params={"content_type": 5},
)

step_send_jpeg_put_request_to_second = Step(
    function="modem.http.put",
    name="send_jpeg_put_request_to_second",
    success="read_response_second",
    fail="failure",
    function_params={"data": "\'test\'"},
)

step_read_response_second = Step(
    function="modem.http.read_response",
    name="read_response_second",
    success="set_server_url_three",
    fail="failure",
)

# Set custom header and send a GET request to server one.
step_set_server_url_3 = Step(
    function="modem.http.set_server_url",
    name="set_server_url_three",
    success="send_get_request",
    fail="failure",
    function_params={"url": f"'{SERVER_URL_1}'"},
)

step_send_get_request = Step(
    function="modem.http.get",
    name="send_get_request",
    success="read_response_third",
    fail="failure",
)

step_read_response_third = Step(
    function="modem.http.read_response",
    name="read_response_third",
    success="success",
    fail="failure",
    retry=3,
    interval=1
)


# Add those steps into state manager.
state_manager = TesterManager(step_network_reg, TEST_NAME)
state_manager.add_step(step_network_reg)
state_manager.add_step(step_pdp_ready)
state_manager.add_step(step_set_context)

state_manager.add_step(step_set_server_url_1)
state_manager.add_step(step_set_content_type_1)
state_manager.add_step(step_send_json_post_request_to_first)
state_manager.add_step(step_read_response_zeroth)

state_manager.add_step(step_set_server_url_2)
state_manager.add_step(step_send_json_post_request_to_second)
state_manager.add_step(step_read_response_first)

state_manager.add_step(step_set_content_type_2)
state_manager.add_step(step_send_jpeg_put_request_to_second)
state_manager.add_step(step_read_response_second)

state_manager.add_step(step_set_server_url_3)
state_manager.add_step(step_send_get_request)
state_manager.add_step(step_read_response_third)
