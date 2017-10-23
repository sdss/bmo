
from functools import wraps


def check_connection(function):
    """Checks device connection."""

    @wraps(function)
    def wrapper(self, user_cmd=None, **kwargs):
        return self._check_connection(function, user_cmd=user_cmd, retry=True, **kwargs)

    return wrapper
