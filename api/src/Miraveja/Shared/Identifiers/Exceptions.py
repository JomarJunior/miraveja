from Miraveja.Shared.Errors.Models import DomainException


class InvalidUUIDException(DomainException):
    def __init__(self, id: str) -> None:
        super().__init__(f"ID '{id}' is not a valid UUID4 string.")
