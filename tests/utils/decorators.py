import requests
from functools import wraps
from typing import Callable, TypeVar, Any

# Define a generic type for the function
F = TypeVar('F', bound=Callable[..., Any])


def handle_requests_exceptions(func: F) -> F:
    """Requests Exceptions handle decorator"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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

    return wrapper  # type: ignore