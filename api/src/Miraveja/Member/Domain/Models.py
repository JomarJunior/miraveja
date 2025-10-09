from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field

from Miraveja.Member.Domain.Exceptions import (
    MissingEmailException,
    MissingFirstNameException,
    MissingLastNameException,
)
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser


class Member(BaseModel):
    """
    Model representing a member with an ID, email, and name.
    """

    # These fields come from Keycloak and should represent all necessary user info
    id: MemberId
    email: EmailStr
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)

    # These fields are specific to our application
    # The member should be able to be registered with default values for them
    registeredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def Register(cls, id: MemberId, email: EmailStr, firstName: str, lastName: str) -> "Member":
        """
        Registers a new Member entity.

        Args:
            id: The member's unique identifier, this should come from Keycloak
            email: The member's email address
            firstName: The member's first name
            lastName: The member's last name

        Returns:
            A new Member instance
        """
        return cls(
            id=id,
            email=email,
            firstName=firstName,
            lastName=lastName,
        )

    @classmethod
    def CreateFromKeycloakUser(cls, keycloakUser: KeycloakUser) -> "Member":
        """
        Creates a Member entity from a KeycloakUser object.

        Args:
            keycloakUser: The authenticated Keycloak user information

        Returns:
            A new Member instance

        Raises:
            MissingEmailException: When Keycloak user has no email
            MissingFirstNameException: When Keycloak user has no first name
            MissingLastNameException: When Keycloak user has no last name
            InvalidEmailException: When Keycloak user's email is not valid
        """
        if not keycloakUser.email:
            raise MissingEmailException()
        if not keycloakUser.firstName:
            raise MissingFirstNameException()
        if not keycloakUser.lastName:
            raise MissingLastNameException()

        return cls(
            id=MemberId(id=keycloakUser.id),
            email=keycloakUser.email,
            firstName=keycloakUser.firstName,
            lastName=keycloakUser.lastName,
        )

    @classmethod
    def FromDatabase(
        cls,
        id: str,
        email: str,
        firstName: str,
        lastName: str,
        registeredAt: datetime,
        updatedAt: datetime,
    ) -> "Member":
        """
        Creates a Member entity from database fields.

        Args:
            id: The member's unique identifier
            email: The member's email address
            firstName: The member's first name
            lastName: The member's last name
            registeredAt: The datetime when the member registered
            updatedAt: The datetime when the member was last updated
        Returns:
            A new Member instance

        Examples:
            `member = Member.FromDatabase(**db_record)` <- db_record is a dict with keys matching the parameters
        """
        return cls(
            id=MemberId(id=id),
            email=email,
            firstName=firstName,
            lastName=lastName,
            registeredAt=registeredAt,
            updatedAt=updatedAt,
        )
