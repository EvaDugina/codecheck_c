import time
from functools import wraps


def time_decorator(function):
    @wraps(function)
    def time_decorator(*args, **kwargs):
        start = time.perf_counter()
        result = function(*args, **kwargs)
        runtime = time.perf_counter() - start
        message = f"====\nвремя: {runtime:.1f} сек"

        print(message)

        return result

    return time_decorator
