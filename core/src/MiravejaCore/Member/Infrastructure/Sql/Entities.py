from datetime import datetime
from typing import Any, Dict

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from MiravejaCore.Member.Domain.Models import Member

Base = declarative_base()


class MemberEntity(Base):
    __tablename__ = "t_member"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=sa.text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)

    # Profile fields
    username: Mapped[str] = mapped_column(sa.String(41), unique=True, nullable=True)
    bio: Mapped[str] = mapped_column(sa.String(500), nullable=False, server_default="")
    avatarId: Mapped[int | None] = mapped_column("avatar_id", sa.Integer(), nullable=True)
    coverId: Mapped[int | None] = mapped_column("cover_id", sa.Integer(), nullable=True)

    # Identity fields
    firstName: Mapped[str] = mapped_column("first_name", sa.String(50), nullable=False)
    lastName: Mapped[str] = mapped_column("last_name", sa.String(50), nullable=False)
    gender: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    dateOfBirth: Mapped[datetime | None] = mapped_column("date_of_birth", sa.DateTime(timezone=True), nullable=True)

    # Social fields (stored as JSONB arrays of UUIDs)
    friends: Mapped[list] = mapped_column(sa.JSON(), nullable=False, server_default="[]")
    followers: Mapped[list] = mapped_column(sa.JSON(), nullable=False, server_default="[]")
    following: Mapped[list] = mapped_column(sa.JSON(), nullable=False, server_default="[]")

    # Member state
    isActive: Mapped[bool] = mapped_column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true"))

    # Timestamps
    registeredAt: Mapped[datetime] = mapped_column(
        "registered_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        onupdate=sa.text("now()"),
    )

    def ToDict(self) -> Dict[str, Any]:
        """Convert entity to dictionary matching Member.FromDatabase() parameters."""

        return {
            "id": self.id,
            "email": self.email,
            "username": self.username or "",
            "bio": self.bio,
            "avatarId": self.avatarId,
            "coverId": self.coverId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "gender": self.gender,
            "dateOfBirth": self.dateOfBirth,
            "friends": self.friends or [],
            "followers": self.followers or [],
            "following": self.following or [],
            "isActive": self.isActive,
            "registeredAt": self.registeredAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def FromDomain(cls, domainMember: Member) -> "MemberEntity":
        """Create MemberEntity from Member domain model."""
        return cls(
            id=str(domainMember.id),
            email=domainMember.email,
            username=domainMember.profile.username,
            bio=domainMember.profile.bio,
            avatarId=domainMember.profile.avatarId,
            coverId=domainMember.profile.coverId,
            firstName=domainMember.identity.firstName,
            lastName=domainMember.identity.lastName,
            gender=domainMember.identity.gender,
            dateOfBirth=domainMember.identity.dateOfBirth,
            friends=[str(friendId) for friendId in domainMember.social.friends],
            followers=[str(followerId) for followerId in domainMember.social.followers],
            following=[str(followingId) for followingId in domainMember.social.following],
            isActive=domainMember.isActive,
            registeredAt=domainMember.registeredAt,
            updatedAt=domainMember.updatedAt,
        )
