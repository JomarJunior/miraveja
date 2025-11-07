from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, computed_field, field_serializer

from MiravejaCore.Member.Domain.Events import (
    MemberActivatedEvent,
    MemberAddedFriendEvent,
    MemberDeactivatedEvent,
    MemberFollowedEvent,
    MemberIdentityUpdatedEvent,
    MemberProfileUpdatedEvent,
    MemberRegisteredEvent,
    MemberRemovedFriendEvent,
    MemberUnfollowedEvent,
)
from MiravejaCore.Member.Domain.Exceptions import (
    MissingEmailException,
    MissingFirstNameException,
    MissingLastNameException,
    MissingUsernameException,
)
from MiravejaCore.Shared.Events.Domain.Models import EventEmitter
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, MemberId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser


class Profile(BaseModel):
    """
    Model representing a member's profile information.
    """

    username: str = Field(..., min_length=3, max_length=41)
    bio: str = Field(default="", max_length=500)
    avatarId: Optional[ImageMetadataId] = None
    coverId: Optional[ImageMetadataId] = None


class Identity(BaseModel):
    """
    Model representing a member's identity information.
    """

    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)
    gender: Optional[str] = None
    dateOfBirth: Optional[datetime] = None

    @computed_field
    @property
    def fullName(self) -> str:
        """Returns the full name by combining first and last names."""
        return f"{self.firstName} {self.lastName}"

    def GetAgeAt(self, date: datetime) -> Optional[int]:
        """Calculates the age of the member at a given date."""
        if self.dateOfBirth is None:
            return None
        age = date.year - self.dateOfBirth.year
        if (date.month, date.day) < (self.dateOfBirth.month, self.dateOfBirth.day):
            age -= 1
        return age


class Social(BaseModel):
    """
    Model representing a member's social interactions.
    """

    friends: List[MemberId] = Field(default_factory=list)
    followers: List[MemberId] = Field(default_factory=list)
    following: List[MemberId] = Field(default_factory=list)


class Member(EventEmitter):
    """
    Model representing a member with an ID, email, and name.
    """

    id: MemberId
    email: EmailStr
    profile: Profile = Field(..., description="Profile information of the member")
    identity: Identity = Field(..., description="Identity information of the member")
    social: Social = Field(default_factory=Social, description="Social interactions of the member")

    isActive: bool = Field(default=True, description="Indicates if the member is active")

    registeredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("registeredAt", "updatedAt")
    def SerializeDatetime(self, value: datetime) -> str:
        """Serializes datetime fields to ISO 8601 format."""
        return value.isoformat()

    @classmethod
    def Register(
        cls,
        id: MemberId,
        email: str,
        username: str,
        bio: str,
        avatarId: Optional[ImageMetadataId],
        coverId: Optional[ImageMetadataId],
        firstName: str,
        lastName: str,
        gender: Optional[str] = None,
        dateOfBirth: Optional[datetime] = None,
    ) -> "Member":
        """
        Registers a new Member entity.

        Args:
            id: The member's unique identifier, this should come from Keycloak
            email: The member's email address
            username: The member's username
            bio: The member's bio
            avatarId: The member's avatar image ID
            coverId: The member's cover image ID
            firstName: The member's first name
            lastName: The member's last name
            gender: The member's gender
            dateOfBirth: The member's date of birth

        Returns:
            A new Member instance
        """

        newMember = cls(
            id=id,
            email=email,
            profile=Profile(
                username=username,
                bio=bio,
                avatarId=avatarId,
                coverId=coverId,
            ),
            identity=Identity(
                firstName=firstName,
                lastName=lastName,
                gender=gender,
                dateOfBirth=dateOfBirth,
            ),
        )

        newMember.EmitEvent(MemberRegisteredEvent.FromModel(newMember))

        return newMember

    @classmethod
    def RegisterFromKeycloakUser(
        cls,
        keycloakUser: KeycloakUser,
        bio: str = "",
        avatarId: Optional[ImageMetadataId] = None,
        coverId: Optional[ImageMetadataId] = None,
        gender: Optional[str] = None,
        dateOfBirth: Optional[datetime] = None,
    ) -> "Member":
        """
        Registers a new Member entity from Keycloak user information.

        Args:
            keycloakUser: The KeycloakUser instance containing user information
            bio: The member's bio
            avatarId: The member's avatar image ID
            coverId: The member's cover image ID
            gender: The member's gender
            dateOfBirth: The member's date of birth
        Returns:
            A new Member instance
        Raises:
            MissingEmailException: If the email is missing in KeycloakUser
            MissingFirstNameException: If the first name is missing in KeycloakUser
            MissingLastNameException: If the last name is missing in KeycloakUser
            MissingUsernameException: If the username is missing in KeycloakUser
        """
        if not keycloakUser.email:
            raise MissingEmailException()
        if not keycloakUser.firstName:
            raise MissingFirstNameException()
        if not keycloakUser.lastName:
            raise MissingLastNameException()
        if not keycloakUser.username:
            raise MissingUsernameException()

        return cls.Register(
            id=MemberId(id=keycloakUser.id),
            email=keycloakUser.email,
            username=keycloakUser.username,
            firstName=keycloakUser.firstName,
            lastName=keycloakUser.lastName,
            bio=bio,
            avatarId=avatarId,
            coverId=coverId,
            gender=gender,
            dateOfBirth=dateOfBirth,
        )

    @classmethod
    def FromDatabase(
        cls,
        id: str,
        email: str,
        username: str,
        bio: str,
        avatarId: Optional[int],
        coverId: Optional[int],
        firstName: str,
        lastName: str,
        gender: Optional[str],
        dateOfBirth: Optional[datetime],
        friends: List[str],
        followers: List[str],
        following: List[str],
        isActive: bool,
        registeredAt: datetime,
        updatedAt: datetime,
    ) -> "Member":
        """
        Creates a Member entity from database fields.

        Args:
            id: The member's unique identifier
            email: The member's email address
            username: The member's username
            bio: The member's bio
            avatarId: The member's avatar image ID
            coverId: The member's cover image ID
            firstName: The member's first name
            lastName: The member's last name
            gender: The member's gender
            dateOfBirth: The member's date of birth
            friends: The member's friends
            followers: The member's followers
            following: The member's following
            isActive: Whether the member is active
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
            profile=Profile(
                username=username,
                bio=bio,
                avatarId=ImageMetadataId(id=avatarId) if avatarId is not None else None,
                coverId=ImageMetadataId(id=coverId) if coverId is not None else None,
            ),
            identity=Identity(
                firstName=firstName,
                lastName=lastName,
                gender=gender,
                dateOfBirth=dateOfBirth,
            ),
            social=Social(
                friends=[MemberId(id=friendId) for friendId in friends],
                followers=[MemberId(id=followerId) for followerId in followers],
                following=[MemberId(id=followingId) for followingId in following],
            ),
            isActive=isActive,
            registeredAt=registeredAt,
            updatedAt=updatedAt,
        )

    @computed_field
    @property
    def displayName(self) -> str:
        """Returns the display name of the member, which will be shown publicly."""
        return self.profile.username

    def Activate(self):
        """Activates the member account."""
        self.isActive = True
        self.updatedAt = datetime.now(timezone.utc)
        self.EmitEvent(MemberActivatedEvent.FromModel(self))

    def Deactivate(self):
        """Deactivates the member account."""
        self.isActive = False
        self.updatedAt = datetime.now(timezone.utc)
        self.EmitEvent(MemberDeactivatedEvent.FromModel(self))

    def UpdateProfile(self, bio: str, avatarId: Optional[ImageMetadataId], coverId: Optional[ImageMetadataId]):
        """Updates the member's profile information."""
        oldMember = self.model_copy(deep=True)
        self.profile.bio = bio
        self.profile.avatarId = avatarId
        self.profile.coverId = coverId
        self.updatedAt = datetime.now(timezone.utc)
        self.EmitEvent(MemberProfileUpdatedEvent.FromModel(oldMember, self))

    def UpdateIdentity(self, firstName: str, lastName: str, gender: Optional[str], dateOfBirth: Optional[datetime]):
        """Updates the member's identity information."""
        oldMember = self.model_copy(deep=True)
        self.identity.firstName = firstName
        self.identity.lastName = lastName
        self.identity.gender = gender
        self.identity.dateOfBirth = dateOfBirth
        self.updatedAt = datetime.now(timezone.utc)
        self.EmitEvent(MemberIdentityUpdatedEvent.FromModel(oldMember, self))

    def AddFriend(self, memberId: MemberId):
        """Adds a friend to the member's friends list."""
        if memberId not in self.social.friends:
            self.social.friends.append(memberId)
            self.updatedAt = datetime.now(timezone.utc)
            self.EmitEvent(MemberAddedFriendEvent.FromMembersIds(self.id, memberId))

    def RemoveFriend(self, memberId: MemberId):
        """Removes a friend from the member's friends list."""
        if memberId in self.social.friends:
            self.social.friends.remove(memberId)
            self.updatedAt = datetime.now(timezone.utc)
            self.EmitEvent(MemberRemovedFriendEvent.FromMembersIds(self.id, memberId))

    def FollowMember(self, memberId: MemberId):
        """Follows another member."""
        if memberId not in self.social.following:
            self.social.following.append(memberId)
            self.updatedAt = datetime.now(timezone.utc)
            self.EmitEvent(MemberFollowedEvent.FromMembersIds(self.id, memberId))

    def UnfollowMember(self, memberId: MemberId):
        """Unfollows another member."""
        if memberId in self.social.following:
            self.social.following.remove(memberId)
            self.updatedAt = datetime.now(timezone.utc)
            self.EmitEvent(MemberUnfollowedEvent.FromMembersIds(self.id, memberId))

    def IsFriendWith(self, memberId: MemberId) -> bool:
        """Checks if the member is friends with another member."""
        return memberId in self.social.friends

    def IsFollowing(self, memberId: MemberId) -> bool:
        """Checks if the member is following another member."""
        return memberId in self.social.following

    def IsFollowedBy(self, memberId: MemberId) -> bool:
        """Checks if the member is followed by another member."""
        return memberId in self.social.followers
