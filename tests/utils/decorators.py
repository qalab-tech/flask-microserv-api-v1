import requests
import functools


def handle_requests_exceptions(func):
    """Requests Exceptions handle decorator"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            raise AssertionError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise AssertionError("Failed to connect to the server")
        except requests.exceptions.HTTPError as http_err:
            raise AssertionError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise AssertionError(f"Unexpected error occurred: {err}")

    return wrapper
