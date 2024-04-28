import functools
import sys


def log_output_to_file(filename):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Open the specified file in append mode
            with open(filename, 'a') as f:
                # Redirect standard output to both the file and the console
                class DoubleWriter:
                    def __init__(self, stdout, file):
                        self.stdout = stdout
                        self.file = file

                    def write(self, message):
                        self.stdout.write(message)
                        self.file.write(message)

                    def flush(self):  # flush method is needed when stdout is redirected
                        self.stdout.flush()
                        self.file.flush()

                # Save the current stdout so that we can revert sys.stdout after the function call
                old_stdout = sys.stdout
                sys.stdout = DoubleWriter(old_stdout, f)

                try:
                    # Call the function and capture its output
                    result = func(*args, **kwargs)
                finally:
                    # Ensure that we revert sys.stdout regardless of any error
                    sys.stdout = old_stdout

                return result

        return wrapper

    return decorator
