from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from app.datetime_json import CustomJSONEncoder


class Base(DeclarativeBase):
    pass


class FhirResource(Base):
    __tablename__ = "fhir_resources"

    id: Mapped[uuid.UUID] = mapped_column("id", Uuid, primary_key=True)
    resource_type: Mapped[str] = mapped_column("resource_type", String(64), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column("resource_id", String(256), nullable=False, index=True)
    _data = mapped_column('data', JSONB, nullable=False)

    @property
    def data(self) -> Any:
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        # Serialize the data using the custom encoder before saving
        self._data = json.loads(json.dumps(value, cls=CustomJSONEncoder))

    def __repr__(self) -> str:
        return f"<FhirResource(id={self.id}, resource_type={self.resource_type}, resource_id={self.resource_id})>"


class FhirReference(Base):
    __tablename__ = "fhir_references"

    id: Mapped[uuid.UUID] = mapped_column("id", Uuid, primary_key=True)
    pseudonym: Mapped[uuid.UUID] = mapped_column("pseudonym", Uuid, nullable=False, index=True)
    references = mapped_column("references", JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"<FhirReference(id={self.id}, pseudonym={self.pseudonym})>"