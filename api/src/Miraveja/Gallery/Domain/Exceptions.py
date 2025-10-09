from Miraveja.Shared.Errors.Models import DomainException
from Miraveja.Shared.Identifiers.Models import ImageMetadataId


class MalformedImageSizeStringException(DomainException):
    """Exception raised for invalid image size."""

    def __init__(self, sizeString: str):
        message = f"Malformed size string: '{sizeString}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        super().__init__(message, code=400, details={"sizeString": sizeString})


class ImageMetadataNotFoundException(DomainException):
    """Exception raised when an image metadata is not found."""

    def __init__(self, imageId: ImageMetadataId):
        message = f"Image metadata with ID '{imageId}' was not found."
        super().__init__(message, code=404, details={"imageId": imageId})


class ImageMetadataAlreadyExistsException(DomainException):
    """Exception raised when attempting to register an image metadata that already exists."""

    def __init__(self, imageId: ImageMetadataId):
        message = f"Image metadata with ID '{imageId}' already exists."
        super().__init__(message, code=409, details={"imageId": imageId})


class ImageMetadataUriAlreadyExistsException(DomainException):
    """Exception raised when attempting to register an image metadata with a URI that already exists."""

    def __init__(self, uri: str):
        message = f"Image metadata with URI '{uri}' already exists."
        super().__init__(message, code=409, details={"uri": uri})
