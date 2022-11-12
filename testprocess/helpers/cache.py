"""
To store the states for caching purposes.
"""


class StateCache:
    """Data class for storing state data."""

    states = {}
    last_response = None

    def add_cache(self, function_name):
        """Gets cache for #function_name or adds
        new cache with #function_name key
        """
        self.states[function_name] = None

    def get_state(self, function_name):
        """Returns state of function_name"""
        return self.states.get(function_name)

    def set_state(self, function_name, state):
        """Sets state of function_name"""
        self.states[function_name] = state

    def get_last_response(self):
        """Returns last response"""
        return self.last_response

    def set_last_response(self, response):
        """Sets last response"""
        self.last_response = response


cache = StateCache()
