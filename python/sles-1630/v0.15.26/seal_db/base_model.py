import uuid

from pydantic import AwareDatetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

ID = uuid.UUID


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[ID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    created_on: Mapped[AwareDatetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), index=True
    )

    updated_on: Mapped[AwareDatetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        index=True,
    )
