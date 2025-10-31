from Miraveja.Shared.Errors.Models import DomainException


class ImageContentTooLargeException(DomainException):
    def __init__(self, maxSizeBytes: int, actualSizeBytes: int):
        message = (
            f"Image content size {actualSizeBytes} bytes exceeds the maximum allowed size of {maxSizeBytes} bytes."
        )
        super().__init__(message, code=413)  # 413 Payload Too Large


class UnsupportedImageMimeTypeException(DomainException):
    def __init__(self, mimeType: str):
        message = f"Unsupported image MIME type: '{mimeType}'."
        super().__init__(message, code=415)  # 415 Unsupported Media Type


class ImageNotValidException(DomainException):
    def __init__(self):
        message = "The provided binary content is not a valid image."
        super().__init__(message, code=422)  # 422 Unprocessable Entity
