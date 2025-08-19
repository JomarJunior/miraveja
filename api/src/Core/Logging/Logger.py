import os
import inspect
from datetime import datetime
from random import randbytes
import zipfile

class Logger():
    """
    This class provides logging functionality for the application.
    """

    def __init__(self, target: str = "console"):
        """
        Initialize the logger with a target.
        :param target: The target for logging, e.g., 'console', 'file'.
        """
        self.target = target
        self.latest_caller_sent = None
        if self.target != "console":
            os.makedirs(os.path.dirname(self.target), exist_ok=True)
            # Concat general.log to the target file if it is a file path
            if not self.target.endswith('.log'):
                self.target = os.path.join(self.target, 'general.log')

    def _log(self, message: str):
        """
        Internal method to log a message to the specified target.
        :param message: The message to log.
        """
        message = self._prepend_current_time(message)
        message = self._prepend_caller_info(message)
        if self.target == "console":
            print(message)
        else:
            self._log_rotate()
            if not os.path.exists(self.target):
                os.makedirs(os.path.dirname(self.target), exist_ok=True)
            with open(self.target, 'a', encoding='utf-8') as file:
                file.write(message + '\n')

    def _log_rotate(self):
        """
        Rotate the log file if it exceeds a certain size.
        """
        max_log_size = 1024 * 1024 * 5  # 5 MB
        if self.target != "console" and os.path.exists(self.target):
            if os.path.getsize(self.target) > max_log_size:
                # Rotate the log file by renaming it and creating a new one
                month_name: str = datetime.now().strftime("%B")
                random_bytes = randbytes(8).hex()
                new_name: str = f"{self.target}.{month_name}.{random_bytes}"
                os.rename(self.target, new_name)
                with open(self.target, 'w', encoding='utf-8') as file:
                    file.write("")
                # Compress the old log
                with zipfile.ZipFile(f"{new_name}.zip", 'w') as zipf:
                    zipf.write(new_name, arcname=os.path.basename(new_name))
                os.remove(new_name)

    def _prepend_current_time(self, message: str) -> str:
        """
        Prepend the current time to the log message.
        :param message: The original log message.
        :return: The modified log message with the current time.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{current_time}] {message}"

    def _prepend_caller_info(self, message: str) -> str:
        """
        Prepend caller information to the log message.
        Here we usually arrive three levels up the stack to get the caller function name and file information.
        This helps in identifying where the log message originated from.
        :param message: The original log message.
        :return: The modified log message with caller information.
        """
        # Get the current frame and the caller frame (skip the _prepend_caller_info method, the _log method and the specific level method)
        current_frame = inspect.currentframe()
        if current_frame is not None:
            # Skip the current frame
            caller_frame = current_frame.f_back
            if caller_frame is not None:
                # Skip the _log method
                caller_frame = caller_frame.f_back
            if caller_frame is not None:
                # Get the caller function name and file information
                caller_frame = caller_frame.f_back

            # If we have a valid caller frame, prepend the caller information if it is the first time
            # we are logging from this caller in the sequence of logs
            if caller_frame is not None:
                caller_info = f"{caller_frame.f_code.co_name}() in {caller_frame.f_code.co_filename}"
                # Check if the caller info is already sent
                if self.latest_caller_sent != caller_info:
                    # Update the latest caller info
                    self.latest_caller_sent = caller_info
                    # To avoid excessive logging, we only prepend caller info once per subsequent log
                    return f"{caller_info}\n{message}"
        return message

    def info(self, message: str):
        """
        Log an informational message.
        :param message: The message to log.
        """
        self._log(f"[INFO] - {message}")

    def warning(self, message: str):
        """
        Log a warning message.
        :param message: The message to log.
        """
        self._log(f"[WARNING] - {message}")

    def error(self, message: str):
        """
        Log an error message.
        :param message: The message to log.
        """
        self._log(f"[ERROR] - {message}")

    def debug(self, message: str):
        """
        Log a debug message.
        :param message: The message to log.
        """
        self._log(f"[DEBUG] - {message}")