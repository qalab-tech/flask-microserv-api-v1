import requests
from functools import wraps


def handle_requests_exceptions(func):
    """Requests Exceptions handle decorator"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # If it is a generator (a fixture with yield)
            if hasattr(result, "__iter__") and not isinstance(result, (str, bytes, dict, list)):
                try:
                    yield from result
                finally:
                    if hasattr(result, "close"):
                        result.close()
            return result
        except requests.exceptions.Timeout:
            raise AssertionError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise AssertionError("Failed to connect to the server")
        except requests.exceptions.HTTPError as http_err:
            raise AssertionError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise AssertionError(f"Unexpected error occurred: {err}")

    return wrapper
