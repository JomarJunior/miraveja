from Miraveja.Shared.Errors.Models import DomainException


class DependencyNameNotFoundInContainerException(DomainException):
    def __init__(self, name: str):
        super().__init__(
            message=f"Dependency '{name}' not found in the container.",
            code=500,
            details={"dependency_name": name},
        )
