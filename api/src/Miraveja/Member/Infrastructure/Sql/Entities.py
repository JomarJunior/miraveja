from datetime import datetime
from typing import Any, Dict
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()


class MemberEntity(Base):
    __tablename__ = "t_member"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=sa.text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    firstName: Mapped[str] = mapped_column("first_name", sa.String(50), nullable=False)
    lastName: Mapped[str] = mapped_column("last_name", sa.String(50), nullable=False)
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

    def Update(self, email: str, firstName: str, lastName: str) -> None:
        self.email = email
        self.firstName = firstName
        self.lastName = lastName

    def ToDict(self) -> Dict[str, Any]:
        # The dictionary keys must match the Member model fields
        return {
            "id": self.id,
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "registeredAt": self.registeredAt,
            "updatedAt": self.updatedAt,
        }
