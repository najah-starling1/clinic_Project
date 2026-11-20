# decorators.py
# A decorator is a function that wraps another function to add extra behaviour.
# We have two custom decorators:
#   1. log_action - writes every appointment operation to a log file
#   2. time_it    - shows how long a report takes to generate

import os
import time
from datetime import datetime

# the project folder (one level above this file)
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FOLDER = os.path.join(PROJECT_FOLDER, "logs")


def log_action(func):
    """Writes a line to logs/clinic_log.txt each time the function runs."""
    def wrapper(*args, **kwargs):
        os.makedirs(LOG_FOLDER, exist_ok=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            result = func(*args, **kwargs)
            message = now + " | " + func.__name__ + " | SUCCESS"
            return result
        except ValueError as error:
            message = now + " | " + func.__name__ + " | FAILED: " + str(error)
            raise  # pass the error on so the menu can show it
        finally:
            with open(os.path.join(LOG_FOLDER, "clinic_log.txt"), "a") as log_file:
                log_file.write(message + "\n")
    return wrapper


def time_it(func):
    """Prints how many milliseconds the function took."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("(Report generated in " + str(round((end - start) * 1000, 2)) + " ms)")
        return result
    return wrapper
