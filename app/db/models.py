from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ResourceEntry(Base):
    __tablename__ = "resource_entry"

    id: Mapped[uuid.UUID] = mapped_column("id", Uuid, primary_key=True)
    pseudonym: Mapped[uuid.UUID] = mapped_column("pseudonym", Uuid, index=True)
    resource_type: Mapped[str] = mapped_column("resource_type", String(64), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column("resource_id", String(256), nullable=False, index=True)
    resource = mapped_column("resource", JSON, nullable=False)
    version: Mapped[int] = mapped_column("version", Integer, nullable=False, default=1)
    created_dt: Mapped[datetime] = mapped_column("created_dt", DateTime, nullable=False, default=datetime.utcnow)
    deleted: Mapped[bool] = mapped_column("deleted", Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<FhirResource(id={self.id}, resource_type={self.resource_type}, resource_id={self.resource_id})>"
