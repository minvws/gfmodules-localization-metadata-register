import uuid
from datetime import datetime

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
            # Create a new resource entry instance with the next version
            entry = ResourceEntry(
                id=uuid.uuid4(),
                pseudonym=uuid.UUID(str(pseudonym)),
                resource_type=resource_type,
                resource_id=resource_id,
                resource=data,
                version=1,
                created_dt=datetime.now(),
                deleted=False,
            )

            subquery = (
                self.db_session.query(func.coalesce(func.max(ResourceEntry.version), 0) + 1)
                .filter(ResourceEntry.resource_id == resource_id and ResourceEntry.resource_type == resource_type)
            ).scalar_subquery()

            from sqlalchemy.dialects.postgresql import insert
            insert_stmt = insert(ResourceEntry).values(
                id=entry.id,
                pseudonym=entry.pseudonym,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                resource=entry.resource,
                version=entry.version,
                created_dt=entry.created_dt,
                deleted=entry.deleted
            ).on_conflict_do_update(
                constraint='resource_type_id',
                set_ = { 'version': subquery }
            )
            self.db_session.execute(insert_stmt)

            return entry
