"""Wrappers for functions."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import requests


def retry(
    max_retries: int = 3, delay: float = 1, rate_limit_delay: float = 60
) -> Callable:
    """A wrapper that retries a function.

    Note:
        - For 429 errors, waits for the 'Retry-After' header value if present, otherwise uses rate_limit_delay.
        - For 400 errors, does not retry and raises the exception immediately.

    Args:
        max_retries (int): Maximum number of retries. Default is 3.
        delay (float): Delay in seconds between retries. Default is 1.
        rate_limit_delay (float): Delay in seconds for rate limiting. Default is 60 (1 minute).

    Returns:
        Callable: The decorated function with retry logic.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)  # Preserves func metadata
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Callable:
            # Running through attempts
            for attempt in range(1, max_retries + 1):
                # Try to call the function
                try:
                    return func(*args, **kwargs)
                # Except HTTP errors (status codes other than 200)
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code

                    # Check for specific status codes
                    if status_code == 429:
                        retry_after = e.response.headers.get("Retry-After")
                        wait_time = (
                            int(retry_after) if retry_after else rate_limit_delay
                        )
                        print(
                            f"Rate limited (429). Waiting {wait_time} seconds before retrying..."
                        )
                        time.sleep(wait_time)

                    elif status_code == 400:
                        print(f"Bad request (400). Not retrying. Error: {e}")
                        raise

                    # Other HTTP errors
                    else:
                        print(f"Attempt {attempt} failed: {e}")
                        if attempt < max_retries:
                            time.sleep(delay)
                        else:
                            print("Max retries reached. Raising exception.")
                            raise

                # General exceptions
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
                    else:
                        print("Max retries reached. Raising exception.")
                        raise

            raise RuntimeError(
                "Retry decorator exhausted without returning or raising."
            )

        return wrapper

    return decorator
