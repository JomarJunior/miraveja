import pytest
from datetime import datetime, timezone
from MiravejaCore.Member.Infrastructure.Sql.Entities import MemberEntity
from MiravejaCore.Member.Domain.Models import Member, Profile, Identity, Social
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Gallery.Domain.Models import ImageMetadataId


class TestMemberEntity:
    """Test cases for MemberEntity SQLAlchemy model."""

    def test_ToDictWithAllFields_ShouldReturnCompleteDict(self):
        """Test that ToDict returns dictionary with all fields populated."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testDateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        testRegisteredAt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        testUpdatedAt = datetime(2024, 6, 1, tzinfo=timezone.utc)

        entity = MemberEntity(
            id=testId,
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            avatarId=123,
            coverId=456,
            firstName="John",
            lastName="Doe",
            gender="Male",
            dateOfBirth=testDateOfBirth,
            friends=["friend-uuid-1", "friend-uuid-2"],
            followers=["follower-uuid-1"],
            following=["following-uuid-1", "following-uuid-2"],
            isActive=True,
            registeredAt=testRegisteredAt,
            updatedAt=testUpdatedAt,
        )

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == testId
        assert result["email"] == "test@example.com"
        assert result["username"] == "testuser"
        assert result["bio"] == "Test bio"
        assert result["avatarId"] == 123
        assert result["coverId"] == 456
        assert result["firstName"] == "John"
        assert result["lastName"] == "Doe"
        assert result["gender"] == "Male"
        assert result["dateOfBirth"] == testDateOfBirth
        assert result["friends"] == ["friend-uuid-1", "friend-uuid-2"]
        assert result["followers"] == ["follower-uuid-1"]
        assert result["following"] == ["following-uuid-1", "following-uuid-2"]
        assert result["isActive"] is True
        assert result["registeredAt"] == testRegisteredAt
        assert result["updatedAt"] == testUpdatedAt

    def test_ToDictWithNullUsername_ShouldReturnEmptyString(self):
        """Test that ToDict returns empty string when username is None."""
        # Arrange
        entity = MemberEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            username=None,
            bio="Test bio",
            firstName="John",
            lastName="Doe",
            isActive=True,
            registeredAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )

        # Act
        result = entity.ToDict()

        # Assert
        assert result["username"] == ""

    def test_ToDictWithMinimalFields_ShouldReturnDictWithDefaults(self):
        """Test that ToDict handles minimal required fields with appropriate defaults."""
        # Arrange
        testRegisteredAt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        testUpdatedAt = datetime(2024, 6, 1, tzinfo=timezone.utc)

        entity = MemberEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            username="testuser",
            bio="",
            firstName="John",
            lastName="Doe",
            isActive=True,
            registeredAt=testRegisteredAt,
            updatedAt=testUpdatedAt,
        )

        # Act
        result = entity.ToDict()

        # Assert
        assert result["avatarId"] is None
        assert result["coverId"] is None
        assert result["gender"] is None
        assert result["dateOfBirth"] is None
        assert result["friends"] == []
        assert result["followers"] == []
        assert result["following"] == []

    def test_ToDictWithNullSocialLists_ShouldReturnEmptyLists(self):
        """Test that ToDict returns empty lists when social fields are None."""
        # Arrange
        entity = MemberEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            firstName="John",
            lastName="Doe",
            friends=None,
            followers=None,
            following=None,
            isActive=True,
            registeredAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )

        # Act
        result = entity.ToDict()

        # Assert
        assert result["friends"] == []
        assert result["followers"] == []
        assert result["following"] == []

    def test_FromDomainWithAllFields_ShouldCreateEntityCorrectly(self):
        """Test that FromDomain creates entity from complete domain model."""
        # Arrange
        memberId = MemberId.Generate()
        testDateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        testRegisteredAt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        testUpdatedAt = datetime(2024, 6, 1, tzinfo=timezone.utc)

        friendId1 = MemberId.Generate()
        friendId2 = MemberId.Generate()
        followerId = MemberId.Generate()
        followingId1 = MemberId.Generate()
        followingId2 = MemberId.Generate()

        domainMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(
                username="testuser",
                bio="Test bio",
                avatarId=ImageMetadataId(id=123),
                coverId=ImageMetadataId(id=456),
            ),
            identity=Identity(
                firstName="John",
                lastName="Doe",
                gender="Male",
                dateOfBirth=testDateOfBirth,
            ),
            social=Social(
                friends=[friendId1, friendId2],
                followers=[followerId],
                following=[followingId1, followingId2],
            ),
            isActive=True,
            registeredAt=testRegisteredAt,
            updatedAt=testUpdatedAt,
        )

        # Act
        entity = MemberEntity.FromDomain(domainMember)

        # Assert
        assert entity.id == str(memberId)
        assert entity.email == "test@example.com"
        assert entity.username == "testuser"
        assert entity.bio == "Test bio"
        assert entity.avatarId == ImageMetadataId(id=123)
        assert entity.coverId == ImageMetadataId(id=456)
        assert entity.firstName == "John"
        assert entity.lastName == "Doe"
        assert entity.gender == "Male"
        assert entity.dateOfBirth == testDateOfBirth
        assert entity.friends == [str(friendId1), str(friendId2)]
        assert entity.followers == [str(followerId)]
        assert entity.following == [str(followingId1), str(followingId2)]
        assert entity.isActive is True
        assert entity.registeredAt == testRegisteredAt
        assert entity.updatedAt == testUpdatedAt

    def test_FromDomainWithMinimalFields_ShouldCreateEntityWithDefaults(self):
        """Test that FromDomain handles minimal domain model with optional fields as None."""
        # Arrange
        memberId = MemberId.Generate()

        domainMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        entity = MemberEntity.FromDomain(domainMember)

        # Assert
        assert entity.id == str(memberId)
        assert entity.email == "test@example.com"
        assert entity.username == "testuser"
        assert entity.bio == ""
        assert entity.avatarId is None
        assert entity.coverId is None
        assert entity.firstName == "John"
        assert entity.lastName == "Doe"
        assert entity.gender is None
        assert entity.dateOfBirth is None
        assert entity.friends == []
        assert entity.followers == []
        assert entity.following == []
        assert entity.isActive is True

    def test_FromDomainWithEmptySocialLists_ShouldCreateEntityWithEmptyArrays(self):
        """Test that FromDomain converts empty social lists correctly."""
        # Arrange
        memberId = MemberId.Generate()

        domainMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
            social=Social(friends=[], followers=[], following=[]),
        )

        # Act
        entity = MemberEntity.FromDomain(domainMember)

        # Assert
        assert entity.friends == []
        assert entity.followers == []
        assert entity.following == []

    def test_FromDomainWithImageIds_ShouldStoreImageMetadataIds(self):
        """Test that FromDomain stores ImageMetadataId objects correctly."""
        # Arrange
        memberId = MemberId.Generate()
        avatarId = ImageMetadataId(id=789)
        coverId = ImageMetadataId(id=101112)

        domainMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(
                username="testuser",
                avatarId=avatarId,
                coverId=coverId,
            ),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        entity = MemberEntity.FromDomain(domainMember)

        # Assert
        assert entity.avatarId == avatarId
        assert entity.coverId == coverId
        assert isinstance(entity.avatarId, ImageMetadataId)
        assert isinstance(entity.coverId, ImageMetadataId)

    def test_FromDomainRoundTripWithToDict_ShouldPreserveData(self):
        """Test that converting from domain to entity and back to dict preserves data."""
        # Arrange
        memberId = MemberId.Generate()
        friendId = MemberId.Generate()
        testDateOfBirth = datetime(1990, 5, 15, tzinfo=timezone.utc)
        testRegisteredAt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        testUpdatedAt = datetime(2024, 6, 1, tzinfo=timezone.utc)

        domainMember = Member(
            id=memberId,
            email="roundtrip@example.com",
            profile=Profile(
                username="roundtripuser",
                bio="Roundtrip bio",
                avatarId=ImageMetadataId(id=999),
            ),
            identity=Identity(
                firstName="Jane",
                lastName="Smith",
                gender="Female",
                dateOfBirth=testDateOfBirth,
            ),
            social=Social(friends=[friendId]),
            isActive=False,
            registeredAt=testRegisteredAt,
            updatedAt=testUpdatedAt,
        )

        # Act
        entity = MemberEntity.FromDomain(domainMember)
        result = entity.ToDict()

        # Assert
        assert result["id"] == str(memberId)
        assert result["email"] == "roundtrip@example.com"
        assert result["username"] == "roundtripuser"
        assert result["bio"] == "Roundtrip bio"
        assert result["avatarId"] == ImageMetadataId(id=999)
        assert result["coverId"] is None
        assert result["firstName"] == "Jane"
        assert result["lastName"] == "Smith"
        assert result["gender"] == "Female"
        assert result["dateOfBirth"] == testDateOfBirth
        assert result["friends"] == [str(friendId)]
        assert result["followers"] == []
        assert result["following"] == []
        assert result["isActive"] is False
        assert result["registeredAt"] == testRegisteredAt
        assert result["updatedAt"] == testUpdatedAt
