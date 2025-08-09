class BaseException(Exception):
    """
    Base class for all custom exceptions in the application.
    """
    def __init__(self, title: str, message: str, code: int = 500):
        super().__init__(message)
        self.title = title
        self.code = code