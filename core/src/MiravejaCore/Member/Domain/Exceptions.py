from MiravejaCore.Shared.Errors.Models import DomainException


class InvalidEmailException(DomainException):
    def __init__(self, email: str):
        super().__init__(f"The email '{email}' is not valid.")


class MissingEmailException(DomainException):
    def __init__(self):
        super().__init__("Email is required but was not provided.")


class MissingFirstNameException(DomainException):
    def __init__(self):
        super().__init__("First name is required but was not provided.")


class MissingLastNameException(DomainException):
    def __init__(self):
        super().__init__("Last name is required but was not provided.")


class MissingUsernameException(DomainException):
    def __init__(self):
        super().__init__("Username is required but was not provided.")


class MemberNotFoundException(DomainException):
    def __init__(self, memberId: str):
        super().__init__(f"Member with ID '{memberId}' was not found.")


class MemberAlreadyExistsException(DomainException):
    def __init__(self, memberId: str):
        super().__init__(f"Member with ID '{memberId}' already exists.")
