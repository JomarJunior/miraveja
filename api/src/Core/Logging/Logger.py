import os
import inspect

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
        message = self._prepend_caller_info(message)
        if self.target == "console":
            print(message)
        else:
            if not os.path.exists(self.target):
                os.makedirs(os.path.dirname(self.target), exist_ok=True)
            with open(self.target, 'a', encoding='utf-8') as file:
                file.write(message + '\n')
    
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