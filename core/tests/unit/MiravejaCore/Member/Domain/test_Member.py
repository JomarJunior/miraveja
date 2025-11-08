import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from MiravejaCore.Member.Domain.Models import Member, Profile, Identity, Social
from MiravejaCore.Shared.Identifiers.Exceptions import InvalidUUIDException
from MiravejaCore.Shared.Identifiers.Models import MemberId, ImageMetadataId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Member.Domain.Exceptions import (
    MissingEmailException,
    MissingFirstNameException,
    MissingLastNameException,
    MissingUsernameException,
)


class TestMember:
    """Test cases for Member domain model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that Member initializes with valid data."""
        memberId = MemberId.Generate()
        email = "test@example.com"
        username = "testuser"
        firstName = "John"
        lastName = "Doe"

        member = Member(
            id=memberId,
            email=email,
            profile=Profile(username=username),
            identity=Identity(firstName=firstName, lastName=lastName),
        )

        assert member.id == memberId
        assert member.email == email
        assert member.profile.username == username
        assert member.identity.firstName == firstName
        assert member.identity.lastName == lastName
        assert isinstance(member.registeredAt, datetime)
        assert isinstance(member.updatedAt, datetime)
        assert member.registeredAt.tzinfo == timezone.utc
        assert member.updatedAt.tzinfo == timezone.utc
        assert member.isActive is True

    def test_InitializeWithCustomTimestamps_ShouldSetCorrectValues(self):
        """Test that Member accepts custom timestamps."""
        memberId = MemberId.Generate()
        registeredAt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updatedAt = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            registeredAt=registeredAt,
            updatedAt=updatedAt,
        )

        assert member.registeredAt == registeredAt
        assert member.updatedAt == updatedAt

    def test_InitializeWithEmptyFirstName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with empty first name."""
        memberId = MemberId.Generate()

        with pytest.raises(ValidationError) as excInfo:
            Member(
                id=memberId,
                email="test@example.com",
                profile=Profile(username="testuser"),
                identity=Identity(firstName="", lastName="Doe"),
            )

        assert "at least 1 character" in str(excInfo.value)

    def test_InitializeWithTooLongFirstName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with first name too long."""
        memberId = MemberId.Generate()
        longName = "a" * 51  # Exceeds 50 character limit

        with pytest.raises(ValidationError) as excInfo:
            Member(
                id=memberId,
                email="test@example.com",
                profile=Profile(username="testuser"),
                identity=Identity(firstName=longName, lastName="Doe"),
            )

        assert "at most 50 character" in str(excInfo.value)

    def test_InitializeWithEmptyLastName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with empty last name."""
        memberId = MemberId.Generate()

        with pytest.raises(ValidationError) as excInfo:
            Member(
                id=memberId,
                email="test@example.com",
                profile=Profile(username="testuser"),
                identity=Identity(firstName="John", lastName=""),
            )

        assert "at least 1 character" in str(excInfo.value)

    def test_InitializeWithTooLongLastName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with last name too long."""
        memberId = MemberId.Generate()
        longName = "a" * 51  # Exceeds 50 character limit

        with pytest.raises(ValidationError) as excInfo:
            Member(
                id=memberId,
                email="test@example.com",
                profile=Profile(username="testuser"),
                identity=Identity(firstName="John", lastName=longName),
            )

        assert "at most 50 character" in str(excInfo.value)

    def test_InitializeWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with invalid email."""
        memberId = MemberId.Generate()

        with pytest.raises(ValidationError) as excInfo:
            Member(
                id=memberId,
                email="invalid-email",
                profile=Profile(username="testuser"),
                identity=Identity(firstName="John", lastName="Doe"),
            )

        # Should contain email validation error
        assert "value is not a valid email address" in str(excInfo.value)
        assert "invalid-email" in str(excInfo.value)

    def test_RegisterWithValidData_ShouldCreateMemberWithDefaults(self):
        """Test that Register creates Member with valid data and default timestamps."""
        memberId = MemberId.Generate()
        email = "test@example.com"
        username = "testuser"
        bio = "Test bio"
        firstName = "John"
        lastName = "Doe"

        member = Member.Register(
            id=memberId,
            email=email,
            username=username,
            bio=bio,
            avatarId=None,
            coverId=None,
            firstName=firstName,
            lastName=lastName,
        )

        assert member.id == memberId
        assert member.email == email
        assert member.profile.username == username
        assert member.profile.bio == bio
        assert member.identity.firstName == firstName
        assert member.identity.lastName == lastName
        assert isinstance(member.registeredAt, datetime)
        assert isinstance(member.updatedAt, datetime)

    def test_RegisterFromKeycloakUserWithValidData_ShouldCreateMember(self):
        """Test that RegisterFromKeycloakUser creates Member from valid KeycloakUser."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName="John",
            lastName="Doe",
            emailVerified=True,
        )

        member = Member.RegisterFromKeycloakUser(keycloakUser)

        assert member.id.id == keycloakUser.id
        assert member.email == keycloakUser.email
        assert member.profile.username == keycloakUser.username
        assert member.identity.firstName == keycloakUser.firstName
        assert member.identity.lastName == keycloakUser.lastName

    def test_RegisterFromKeycloakUserWithNoEmail_ShouldRaiseMissingEmailException(self):
        """Test that RegisterFromKeycloakUser raises exception when email is missing."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email=None,
            firstName="John",
            lastName="Doe",
            emailVerified=False,
        )

        with pytest.raises(MissingEmailException):
            Member.RegisterFromKeycloakUser(keycloakUser)

    def test_RegisterFromKeycloakUserWithNoFirstName_ShouldRaiseMissingFirstNameException(self):
        """Test that RegisterFromKeycloakUser raises exception when first name is missing."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName=None,
            lastName="Doe",
            emailVerified=True,
        )

        with pytest.raises(MissingFirstNameException):
            Member.RegisterFromKeycloakUser(keycloakUser)

    def test_RegisterFromKeycloakUserWithNoLastName_ShouldRaiseMissingLastNameException(self):
        """Test that RegisterFromKeycloakUser raises exception when last name is missing."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName="John",
            lastName=None,
            emailVerified=True,
        )

        with pytest.raises(MissingLastNameException):
            Member.RegisterFromKeycloakUser(keycloakUser)

    def test_RegisterFromKeycloakUserWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that RegisterFromKeycloakUser raises exception when email is invalid."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="invalid-email",
            firstName="John",
            lastName="Doe",
            emailVerified=False,
        )

        with pytest.raises(ValidationError):
            Member.RegisterFromKeycloakUser(keycloakUser)

    def test_FromDatabaseWithValidData_ShouldCreateMemberFromDbFields(self):
        """Test that FromDatabase creates Member from database fields."""
        idStr = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        username = "testuser"
        bio = "Test bio"
        firstName = "John"
        lastName = "Doe"
        registeredAt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updatedAt = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        member = Member.FromDatabase(
            id=idStr,
            email=email,
            username=username,
            bio=bio,
            avatarId=None,
            coverId=None,
            firstName=firstName,
            lastName=lastName,
            gender=None,
            dateOfBirth=None,
            friends=[],
            followers=[],
            following=[],
            isActive=True,
            registeredAt=registeredAt,
            updatedAt=updatedAt,
        )

        assert member.id.id == idStr
        assert member.email == email
        assert member.profile.username == username
        assert member.profile.bio == bio
        assert member.identity.firstName == firstName
        assert member.identity.lastName == lastName
        assert member.registeredAt == registeredAt
        assert member.updatedAt == updatedAt
        assert member.isActive is True

    def test_FromDatabaseWithInvalidId_ShouldRaiseValidationError(self):
        """Test that FromDatabase raises validation error with invalid UUID."""
        with pytest.raises(InvalidUUIDException):
            Member.FromDatabase(
                id="invalid-uuid",
                email="test@example.com",
                username="testuser",
                bio="",
                avatarId=None,
                coverId=None,
                firstName="John",
                lastName="Doe",
                gender=None,
                dateOfBirth=None,
                friends=[],
                followers=[],
                following=[],
                isActive=True,
                registeredAt=datetime.now(timezone.utc),
                updatedAt=datetime.now(timezone.utc),
            )

    def test_EqualityWithSameMember_ShouldReturnTrue(self):
        """Test that two Member instances with same data are equal."""
        memberId = MemberId.Generate()
        email = "test@example.com"
        username = "testuser"
        firstName = "John"
        lastName = "Doe"
        timestamp = datetime.now(timezone.utc)

        member1 = Member(
            id=memberId,
            email=email,
            profile=Profile(username=username),
            identity=Identity(firstName=firstName, lastName=lastName),
            registeredAt=timestamp,
            updatedAt=timestamp,
        )

        member2 = Member(
            id=memberId,
            email=email,
            profile=Profile(username=username),
            identity=Identity(firstName=firstName, lastName=lastName),
            registeredAt=timestamp,
            updatedAt=timestamp,
        )

        assert member1 == member2

    def test_EqualityWithDifferentMember_ShouldReturnFalse(self):
        """Test that two Member instances with different data are not equal."""
        member1 = Member(
            id=MemberId.Generate(),
            email="test1@example.com",
            profile=Profile(username="user1"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        member2 = Member(
            id=MemberId.Generate(),
            email="test2@example.com",
            profile=Profile(username="user2"),
            identity=Identity(firstName="Jane", lastName="Smith"),
        )

        assert member1 != member2


class TestIdentity:
    """Test cases for Identity model."""

    def test_FullName_ShouldCombineFirstAndLastNames(self):
        """Test that fullName property combines first and last names."""
        identity = Identity(firstName="John", lastName="Doe")

        assert identity.fullName == "John Doe"

    def test_GetAgeAtWithDateOfBirth_ShouldCalculateCorrectAge(self):
        """Test that GetAgeAt calculates age correctly when date of birth is set."""
        dateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        identity = Identity(firstName="John", lastName="Doe", dateOfBirth=dateOfBirth)

        checkDate = datetime(2024, 5, 20, tzinfo=timezone.utc)
        age = identity.GetAgeAt(checkDate)

        assert age == 34

    def test_GetAgeAtBeforeBirthday_ShouldCalculateCorrectAge(self):
        """Test that GetAgeAt correctly handles dates before birthday in same year."""
        dateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        identity = Identity(firstName="John", lastName="Doe", dateOfBirth=dateOfBirth)

        checkDate = datetime(2024, 5, 10, tzinfo=timezone.utc)  # Before birthday
        age = identity.GetAgeAt(checkDate)

        assert age == 33  # One year less since birthday hasn't occurred yet

    def test_GetAgeAtWithoutDateOfBirth_ShouldReturnNone(self):
        """Test that GetAgeAt returns None when date of birth is not set."""
        identity = Identity(firstName="John", lastName="Doe")

        checkDate = datetime(2024, 5, 20, tzinfo=timezone.utc)
        age = identity.GetAgeAt(checkDate)

        assert age is None


class TestProfile:
    """Test cases for Profile model."""

    def test_InitializeWithUsername_ShouldSetCorrectValues(self):
        """Test that Profile initializes with username."""
        username = "testuser"
        profile = Profile(username=username)

        assert profile.username == username
        assert profile.bio == ""
        assert profile.avatarId is None
        assert profile.coverId is None

    def test_InitializeWithAllFields_ShouldSetCorrectValues(self):
        """Test that Profile initializes with all fields."""
        username = "testuser"
        bio = "Test bio"
        avatarId = ImageMetadataId(id=123)
        coverId = ImageMetadataId(id=456)

        profile = Profile(
            username=username,
            bio=bio,
            avatarId=avatarId,
            coverId=coverId,
        )

        assert profile.username == username
        assert profile.bio == bio
        assert profile.avatarId == avatarId
        assert profile.coverId == coverId


class TestSocial:
    """Test cases for Social model."""

    def test_InitializeWithDefaults_ShouldSetEmptyLists(self):
        """Test that Social initializes with empty lists."""
        social = Social()

        assert social.friends == []
        assert social.followers == []
        assert social.following == []

    def test_InitializeWithLists_ShouldSetCorrectValues(self):
        """Test that Social initializes with provided lists."""
        friend1 = MemberId.Generate()
        follower1 = MemberId.Generate()
        following1 = MemberId.Generate()

        social = Social(
            friends=[friend1],
            followers=[follower1],
            following=[following1],
        )

        assert len(social.friends) == 1
        assert friend1 in social.friends
        assert len(social.followers) == 1
        assert follower1 in social.followers
        assert len(social.following) == 1
        assert following1 in social.following


class TestMemberBehavior:
    """Test cases for Member behavior methods."""

    def test_Activate_ShouldSetIsActiveToTrue(self):
        """Test that Activate sets isActive to True and updates timestamp."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            isActive=False,
        )

        oldUpdatedAt = member.updatedAt
        member.Activate()

        assert member.isActive is True
        assert member.updatedAt >= oldUpdatedAt

    def test_Deactivate_ShouldSetIsActiveToFalse(self):
        """Test that Deactivate sets isActive to False and updates timestamp."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            isActive=True,
        )

        oldUpdatedAt = member.updatedAt
        member.Deactivate()

        assert member.isActive is False
        assert member.updatedAt >= oldUpdatedAt

    def test_UpdateProfile_ShouldUpdateProfileFields(self):
        """Test that UpdateProfile updates profile fields and timestamp."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser", bio="Old bio"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        newBio = "New bio"
        newAvatarId = ImageMetadataId(id=123)
        newCoverId = ImageMetadataId(id=456)
        oldUpdatedAt = member.updatedAt

        member.UpdateProfile(bio=newBio, avatarId=newAvatarId, coverId=newCoverId)

        assert member.profile.bio == newBio
        assert member.profile.avatarId == newAvatarId
        assert member.profile.coverId == newCoverId
        assert member.updatedAt >= oldUpdatedAt

    def test_UpdateIdentity_ShouldUpdateIdentityFields(self):
        """Test that UpdateIdentity updates identity fields and timestamp."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        newFirstName = "Jane"
        newLastName = "Smith"
        newGender = "Female"
        newDateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        oldUpdatedAt = member.updatedAt

        member.UpdateIdentity(
            firstName=newFirstName,
            lastName=newLastName,
            gender=newGender,
            dateOfBirth=newDateOfBirth,
        )

        assert member.identity.firstName == newFirstName
        assert member.identity.lastName == newLastName
        assert member.identity.gender == newGender
        assert member.identity.dateOfBirth == newDateOfBirth
        assert member.updatedAt >= oldUpdatedAt

    def test_AddFriend_ShouldAddToFriendsList(self):
        """Test that AddFriend adds member to friends list."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        friendId = MemberId.Generate()
        oldUpdatedAt = member.updatedAt

        member.AddFriend(friendId)

        assert friendId in member.social.friends
        assert len(member.social.friends) == 1
        assert member.updatedAt >= oldUpdatedAt

    def test_AddFriendAlreadyInList_ShouldNotAddDuplicate(self):
        """Test that AddFriend does not add duplicate when friend already exists."""
        friendId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(friends=[friendId]),
        )

        member.AddFriend(friendId)

        assert len(member.social.friends) == 1

    def test_RemoveFriend_ShouldRemoveFromFriendsList(self):
        """Test that RemoveFriend removes member from friends list."""
        friendId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(friends=[friendId]),
        )

        oldUpdatedAt = member.updatedAt
        member.RemoveFriend(friendId)

        assert friendId not in member.social.friends
        assert len(member.social.friends) == 0
        assert member.updatedAt >= oldUpdatedAt

    def test_RemoveFriendNotInList_ShouldNotRaiseError(self):
        """Test that RemoveFriend handles non-existent friend gracefully."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        nonExistentFriendId = MemberId.Generate()
        member.RemoveFriend(nonExistentFriendId)

        assert len(member.social.friends) == 0

    def test_FollowMember_ShouldAddToFollowingList(self):
        """Test that FollowMember adds member to following list."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        followedId = MemberId.Generate()
        oldUpdatedAt = member.updatedAt

        member.FollowMember(followedId)

        assert followedId in member.social.following
        assert len(member.social.following) == 1
        assert member.updatedAt >= oldUpdatedAt

    def test_FollowMemberAlreadyFollowing_ShouldNotAddDuplicate(self):
        """Test that FollowMember does not add duplicate when already following."""
        followedId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(following=[followedId]),
        )

        member.FollowMember(followedId)

        assert len(member.social.following) == 1

    def test_UnfollowMember_ShouldRemoveFromFollowingList(self):
        """Test that UnfollowMember removes member from following list."""
        followedId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(following=[followedId]),
        )

        oldUpdatedAt = member.updatedAt
        member.UnfollowMember(followedId)

        assert followedId not in member.social.following
        assert len(member.social.following) == 0
        assert member.updatedAt >= oldUpdatedAt

    def test_UnfollowMemberNotFollowing_ShouldNotRaiseError(self):
        """Test that UnfollowMember handles non-followed member gracefully."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        nonFollowedId = MemberId.Generate()
        member.UnfollowMember(nonFollowedId)

        assert len(member.social.following) == 0

    def test_IsFriendWith_ShouldReturnTrueForFriend(self):
        """Test that IsFriendWith returns True for existing friend."""
        friendId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(friends=[friendId]),
        )

        assert member.IsFriendWith(friendId) is True

    def test_IsFriendWith_ShouldReturnFalseForNonFriend(self):
        """Test that IsFriendWith returns False for non-friend."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        nonFriendId = MemberId.Generate()
        assert member.IsFriendWith(nonFriendId) is False

    def test_IsFollowing_ShouldReturnTrueForFollowedMember(self):
        """Test that IsFollowing returns True for followed member."""
        followedId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(following=[followedId]),
        )

        assert member.IsFollowing(followedId) is True

    def test_IsFollowing_ShouldReturnFalseForNonFollowedMember(self):
        """Test that IsFollowing returns False for non-followed member."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        nonFollowedId = MemberId.Generate()
        assert member.IsFollowing(nonFollowedId) is False

    def test_IsFollowedBy_ShouldReturnTrueForFollower(self):
        """Test that IsFollowedBy returns True for existing follower."""
        followerId = MemberId.Generate()
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(followers=[followerId]),
        )

        assert member.IsFollowedBy(followerId) is True

    def test_IsFollowedBy_ShouldReturnFalseForNonFollower(self):
        """Test that IsFollowedBy returns False for non-follower."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        nonFollowerId = MemberId.Generate()
        assert member.IsFollowedBy(nonFollowerId) is False

    def test_DisplayName_ShouldReturnUsername(self):
        """Test that displayName property returns the username."""
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        assert member.displayName == "testuser"

    def test_SerializeDatetime_ShouldReturnIsoFormat(self):
        """Test that datetime serialization returns ISO format."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        member = Member(
            id=MemberId.Generate(),
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            registeredAt=timestamp,
            updatedAt=timestamp,
        )

        serialized = member.model_dump()
        assert serialized["registeredAt"] == "2024-01-15T10:30:00+00:00"
        assert serialized["updatedAt"] == "2024-01-15T10:30:00+00:00"

    def test_RegisterFromKeycloakUserWithEmptyUsername_ShouldRaiseMissingUsernameException(self):
        """Test that RegisterFromKeycloakUser raises exception when username is empty string."""
        keycloakUser = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="",
            email="test@example.com",
            firstName="John",
            lastName="Doe",
            emailVerified=True,
        )

        with pytest.raises(MissingUsernameException):
            Member.RegisterFromKeycloakUser(keycloakUser)

    def test_FromDatabaseWithImageIds_ShouldCreateMemberWithAvatarAndCover(self):
        """Test that FromDatabase creates Member with avatar and cover IDs."""
        member = Member.FromDatabase(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            avatarId=123,
            coverId=456,
            firstName="John",
            lastName="Doe",
            gender=None,
            dateOfBirth=None,
            friends=[],
            followers=[],
            following=[],
            isActive=True,
            registeredAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )

        assert member.profile.avatarId is not None
        assert member.profile.avatarId.id == 123
        assert member.profile.coverId is not None
        assert member.profile.coverId.id == 456

    def test_FromDatabaseWithSocialLists_ShouldCreateMemberWithFriendsFollowersFollowing(self):
        """Test that FromDatabase creates Member with friends, followers, and following."""
        friendId = "550e8400-e29b-41d4-a716-446655440000"
        followerId = "550e8400-e29b-41d4-a716-446655440001"
        followingId = "550e8400-e29b-41d4-a716-446655440002"

        member = Member.FromDatabase(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="John",
            lastName="Doe",
            gender="Male",
            dateOfBirth=datetime(1990, 5, 15, tzinfo=timezone.utc),
            friends=[friendId],
            followers=[followerId],
            following=[followingId],
            isActive=True,
            registeredAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )

        assert len(member.social.friends) == 1
        assert member.social.friends[0].id == friendId
        assert len(member.social.followers) == 1
        assert member.social.followers[0].id == followerId
        assert len(member.social.following) == 1
        assert member.social.following[0].id == followingId
        assert member.identity.gender == "Male"
        assert member.identity.dateOfBirth == datetime(1990, 5, 15, tzinfo=timezone.utc)
