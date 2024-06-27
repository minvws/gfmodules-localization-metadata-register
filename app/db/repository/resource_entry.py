import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy import select, update, func
from typing import Sequence, Any

from app.data import Pseudonym
from app.db.repository import RepositoryBase
from app.db.decorator import repository
from app.db.models import ResourceEntry


@repository(ResourceEntry)
class ResourceEntryRepository(RepositoryBase):
    def find_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[ResourceEntry]:
        stmt = (select(ResourceEntry)
                .where(ResourceEntry.pseudonym == str(pseudonym))
                .where(ResourceEntry.resource_type.ilike(resource_type)))

        return self.db_session.execute(stmt).scalars().all()    # type: ignore

    def find_by_resource(self, resource_type: str, resource_id: str, version: int) -> ResourceEntry | None:
        stmt = (select(ResourceEntry)
                .where(ResourceEntry.resource_type.ilike(resource_type))
                .where(ResourceEntry.resource_id.ilike(resource_id))
                .limit(1))

        if version == 0:
            # Get latest version
            stmt = stmt.order_by(ResourceEntry.version.desc())
        else:
            stmt = stmt.where(ResourceEntry.version == version)

        return self.db_session.execute(stmt).scalars().first()  # type: ignore

    def delete_by_resource(self, resource_type: str, resource_id: str) -> None:
        stmt = (update(ResourceEntry)
                .where(ResourceEntry.resource_type.ilike(resource_type))
                .where(ResourceEntry.resource_id.ilike(resource_id))
                .values(deleted=True))

        self.db_session.execute(stmt)
        self.db_session.commit()

    def upsert(self, resource_type: str, resource_id: str, data: dict[str, Any], pseudonym: Pseudonym) -> ResourceEntry | None:
        with self.db_session.begin():
            if self.db_session.get_dialect() == "postgresql":
                # Advisory lock to prevent concurrent updates
                lock_fn = sqlalchemy.func.pg_advisory_xact_lock(0xdeadbeef)
                self.db_session.execute(sqlalchemy.select(lock_fn))

            # Get the current maximum version
            stmt = (select(func.max(ResourceEntry.version))
                           .where(ResourceEntry.resource_type.ilike(resource_type))
                           .where(ResourceEntry.resource_id.ilike(resource_id)))

            result = self.db_session.execute(stmt)
            max_version = result.scalar()
            next_version = (max_version or 0) + 1

            # Create a new resource entry instance with the next version
            entry = ResourceEntry(
                id=uuid.uuid4(),
                pseudonym=pseudonym,
                resource_type=resource_type,
                resource_id=resource_id,
                resource=data,
                version=next_version,
                created_dt=datetime.now(),
                deleted=False,
            )

            self.db_session.add(entry)
            self.db_session.commit()

            return entry
