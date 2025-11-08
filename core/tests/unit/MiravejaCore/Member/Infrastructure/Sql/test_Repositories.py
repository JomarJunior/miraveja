import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from typing import Iterator

from MiravejaCore.Member.Infrastructure.Sql.Repositories import SqlMemberRepository
from MiravejaCore.Member.Infrastructure.Sql.Entities import MemberEntity
from MiravejaCore.Member.Domain.Models import Member, Profile, Identity, Social
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Repository.Enums import SortOrder


class TestSqlMemberRepository:
    """Test cases for SqlMemberRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create a SqlMemberRepository instance with mocked session."""
        return SqlMemberRepository(dbSession=mock_db_session)

    @pytest.fixture
    def sample_member_dict(self):
        """Create a sample member dictionary for testing."""
        return {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "email": "test@example.com",
            "username": "testuser",
            "bio": "Test bio",
            "avatarId": None,
            "coverId": None,
            "firstName": "John",
            "lastName": "Doe",
            "gender": None,
            "dateOfBirth": None,
            "friends": [],
            "followers": [],
            "following": [],
            "isActive": True,
            "registeredAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        }

    def test_InitializeWithValidSession_ShouldSetCorrectValues(self, mock_db_session):
        """Test that SqlMemberRepository initializes with valid database session."""
        # Arrange & Act
        repository = SqlMemberRepository(dbSession=mock_db_session)

        # Assert
        assert repository._dbSession == mock_db_session

    def test_ListAllWithDefaultQuery_ShouldReturnIteratorOfMembers(
        self, repository, mock_db_session, sample_member_dict
    ):
        """Test that ListAll returns iterator of members with default query parameters."""
        # Arrange
        mockEntity = MagicMock(spec=MemberEntity)
        mockEntity.ToDict.return_value = sample_member_dict

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = [mockEntity]

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.ListAll()

        # Assert
        assert isinstance(result, Iterator)
        memberList = list(result)
        assert len(memberList) == 1
        assert isinstance(memberList[0], Member)
        assert str(memberList[0].id) == "550e8400-e29b-41d4-a716-446655440001"
        assert memberList[0].email == "test@example.com"
        mock_db_session.query.assert_called_once_with(MemberEntity)

    def test_ListAllWithCustomQueryAscending_ShouldApplySortingAndPagination(
        self, repository, mock_db_session, sample_member_dict
    ):
        """Test that ListAll applies custom sorting (ascending) and pagination."""
        # Arrange
        query = ListAllQuery(sortBy="registeredAt", sortOrder=SortOrder.ASC, limit=50, offset=10)

        mockEntity = MagicMock(spec=MemberEntity)
        mockEntity.ToDict.return_value = sample_member_dict

        mockQuery = MagicMock()
        mockSortColumn = MagicMock()
        mockSortColumn.asc.return_value = "sorted_asc"

        # Create a MemberEntity mock that has registeredAt attribute
        with patch.object(MemberEntity, "registeredAt", mockSortColumn):
            mockQuery.order_by.return_value = mockQuery
            mockQuery.offset.return_value = mockQuery
            mockQuery.limit.return_value = mockQuery
            mockQuery.yield_per.return_value = [mockEntity]

            mock_db_session.query.return_value = mockQuery

            # Act
            result = list(repository.ListAll(query=query))

            # Assert
            mockSortColumn.asc.assert_called_once()
            mockQuery.order_by.assert_called_once_with("sorted_asc")
            mockQuery.offset.assert_called_once_with(10)
            mockQuery.limit.assert_called_once_with(50)
            assert len(result) == 1

    def test_ListAllWithCustomQueryDescending_ShouldApplyDescendingSort(
        self, repository, mock_db_session, sample_member_dict
    ):
        """Test that ListAll applies descending sort order."""
        # Arrange
        query = ListAllQuery(sortBy="email", sortOrder=SortOrder.DESC, limit=25, offset=5)

        mockEntity = MagicMock(spec=MemberEntity)
        mockEntity.ToDict.return_value = sample_member_dict

        mockQuery = MagicMock()
        mockSortColumn = MagicMock()
        mockSortColumn.desc.return_value = "sorted_desc"

        # Create a MemberEntity mock that has email attribute
        with patch.object(MemberEntity, "email", mockSortColumn):
            mockQuery.order_by.return_value = mockQuery
            mockQuery.offset.return_value = mockQuery
            mockQuery.limit.return_value = mockQuery
            mockQuery.yield_per.return_value = [mockEntity]

            mock_db_session.query.return_value = mockQuery

            # Act
            result = list(repository.ListAll(query=query))

            # Assert
            mockSortColumn.desc.assert_called_once()
            mockQuery.order_by.assert_called_once_with("sorted_desc")
            mockQuery.offset.assert_called_once_with(5)
            mockQuery.limit.assert_called_once_with(25)
            assert len(result) == 1

    def test_ListAllWithInvalidSortColumn_ShouldSkipSorting(self, repository, mock_db_session):
        """Test that ListAll skips sorting when sort column doesn't exist."""
        # Arrange
        query = ListAllQuery(sortBy="nonExistentColumn", sortOrder=SortOrder.ASC)

        mockQuery = MagicMock()
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = []

        mock_db_session.query.return_value = mockQuery

        # Act
        result = list(repository.ListAll(query=query))

        # Assert
        # order_by should not be called when column doesn't exist on entity
        mockQuery.order_by.assert_not_called()
        mockQuery.offset.assert_called_once()
        mockQuery.limit.assert_called_once()

    def test_ListAllWithFilterFunction_ShouldApplyInMemoryFiltering(
        self, repository, mock_db_session, sample_member_dict
    ):
        """Test that ListAll applies filter function to results."""
        # Arrange
        mockEntity1 = MagicMock(spec=MemberEntity)
        mockEntity1.ToDict.return_value = sample_member_dict

        mockEntity2Dict = sample_member_dict.copy()
        mockEntity2Dict["id"] = "550e8400-e29b-41d4-a716-446655440002"
        mockEntity2Dict["email"] = "inactive@example.com"
        mockEntity2Dict["isActive"] = False
        mockEntity2 = MagicMock(spec=MemberEntity)
        mockEntity2.ToDict.return_value = mockEntity2Dict

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = [mockEntity1, mockEntity2]

        mock_db_session.query.return_value = mockQuery

        # Filter function: only active members
        filterFunc = lambda member: member.isActive

        # Act
        result = list(repository.ListAll(filterFunction=filterFunc))

        # Assert
        assert len(result) == 1
        assert result[0].email == "test@example.com"
        assert result[0].isActive is True

    def test_ListAllWithMultipleEntities_ShouldYieldAllMembers(self, repository, mock_db_session, sample_member_dict):
        """Test that ListAll yields multiple members correctly."""
        # Arrange
        mockEntity1 = MagicMock(spec=MemberEntity)
        mockEntity1.ToDict.return_value = sample_member_dict

        mockEntity2Dict = sample_member_dict.copy()
        mockEntity2Dict["id"] = "550e8400-e29b-41d4-a716-446655440002"
        mockEntity2Dict["email"] = "user2@example.com"
        mockEntity2 = MagicMock(spec=MemberEntity)
        mockEntity2.ToDict.return_value = mockEntity2Dict

        mockEntity3Dict = sample_member_dict.copy()
        mockEntity3Dict["id"] = "550e8400-e29b-41d4-a716-446655440003"
        mockEntity3Dict["email"] = "user3@example.com"
        mockEntity3 = MagicMock(spec=MemberEntity)
        mockEntity3.ToDict.return_value = mockEntity3Dict

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = [mockEntity1, mockEntity2, mockEntity3]

        mock_db_session.query.return_value = mockQuery

        # Act
        result = list(repository.ListAll())

        # Assert
        assert len(result) == 3
        assert result[0].email == "test@example.com"
        assert result[1].email == "user2@example.com"
        assert result[2].email == "user3@example.com"

    def test_Count_ShouldReturnTotalMemberCount(self, repository, mock_db_session):
        """Test that Count returns total number of members in database."""
        # Arrange
        mockQuery = MagicMock()
        mockQuery.count.return_value = 42
        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.Count()

        # Assert
        assert result == 42
        mock_db_session.query.assert_called_once_with(MemberEntity)
        mockQuery.count.assert_called_once()

    def test_CountWithZeroMembers_ShouldReturnZero(self, repository, mock_db_session):
        """Test that Count returns zero when no members exist."""
        # Arrange
        mockQuery = MagicMock()
        mockQuery.count.return_value = 0
        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.Count()

        # Assert
        assert result == 0

    def test_FindByIdWithExistingMember_ShouldReturnMember(self, repository, mock_db_session, sample_member_dict):
        """Test that FindById returns member when entity exists."""
        # Arrange
        memberId = MemberId(id="550e8400-e29b-41d4-a716-446655440001")

        mockEntity = MagicMock(spec=MemberEntity)
        mockEntity.ToDict.return_value = sample_member_dict

        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.FindById(memberId)

        # Assert
        assert result is not None
        assert isinstance(result, Member)
        assert str(result.id) == "550e8400-e29b-41d4-a716-446655440001"
        assert result.email == "test@example.com"
        mock_db_session.get.assert_called_once_with(MemberEntity, str(memberId))

    def test_FindByIdWithNonExistentMember_ShouldReturnNone(self, repository, mock_db_session):
        """Test that FindById returns None when member doesn't exist."""
        # Arrange
        memberId = MemberId(id="550e8400-e29b-41d4-a716-446655440999")
        mock_db_session.get.return_value = None

        # Act
        result = repository.FindById(memberId)

        # Assert
        assert result is None
        mock_db_session.get.assert_called_once_with(MemberEntity, str(memberId))

    def test_MemberExistsWithExistingMember_ShouldReturnTrue(self, repository, mock_db_session):
        """Test that MemberExists returns True when member exists."""
        # Arrange
        memberId = MemberId(id="550e8400-e29b-41d4-a716-446655440001")
        mockEntity = MagicMock(spec=MemberEntity)
        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.MemberExists(memberId)

        # Assert
        assert result is True
        mock_db_session.get.assert_called_once_with(MemberEntity, str(memberId))

    def test_MemberExistsWithNonExistentMember_ShouldReturnFalse(self, repository, mock_db_session):
        """Test that MemberExists returns False when member doesn't exist."""
        # Arrange
        memberId = MemberId(id="550e8400-e29b-41d4-a716-446655440999")
        mock_db_session.get.return_value = None

        # Act
        result = repository.MemberExists(memberId)

        # Assert
        assert result is False
        mock_db_session.get.assert_called_once_with(MemberEntity, str(memberId))

    def test_SaveWithValidMember_ShouldMergeAndCommit(self, repository, mock_db_session):
        """Test that Save merges entity and commits transaction."""
        # Arrange
        member = Member(
            id=MemberId(id="550e8400-e29b-41d4-a716-446655440001"),
            email="save@example.com",
            profile=Profile(username="saveuser"),
            identity=Identity(firstName="Save", lastName="Test"),
        )

        # Act
        repository.Save(member)

        # Assert
        mock_db_session.merge.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    def test_SaveWithDatabaseError_ShouldRollbackAndRaiseException(self, repository, mock_db_session):
        """Test that Save rolls back transaction on database error."""
        # Arrange
        member = Member(
            id=MemberId(id="550e8400-e29b-41d4-a716-446655440001"),
            email="error@example.com",
            profile=Profile(username="erroruser"),
            identity=Identity(firstName="Error", lastName="Test"),
        )

        testException = Exception("Database constraint violation")
        mock_db_session.commit.side_effect = testException

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            repository.Save(member)

        assert str(exc_info.value) == "Database constraint violation"
        mock_db_session.merge.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_called_once()

    def test_SaveWithExistingMember_ShouldUpdateEntity(self, repository, mock_db_session):
        """Test that Save updates existing member (merge handles insert or update)."""
        # Arrange
        memberId = MemberId(id="550e8400-e29b-41d4-a716-446655440001")
        member = Member(
            id=memberId,
            email="updated@example.com",
            profile=Profile(username="updateduser", bio="Updated bio"),
            identity=Identity(firstName="Updated", lastName="User"),
        )

        # Act
        repository.Save(member)

        # Assert
        # Verify that merge was called (merge handles both insert and update)
        assert mock_db_session.merge.call_count == 1
        mergedEntity = mock_db_session.merge.call_args[0][0]
        assert isinstance(mergedEntity, MemberEntity)
        assert mergedEntity.email == "updated@example.com"
        mock_db_session.commit.assert_called_once()
