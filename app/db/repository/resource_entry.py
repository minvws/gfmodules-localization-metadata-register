import uuid
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import func, select, update

from app.data import Pseudonym
from app.db.decorator import repository
from app.db.models import ResourceEntry
from app.db.repository import RepositoryBase


@repository(ResourceEntry)
class ResourceEntryRepository(RepositoryBase):
    def find_by_pseudonym(
        self, pseudonym: Pseudonym, resource_type: str
    ) -> Sequence[ResourceEntry]:
        stmt = (
            select(ResourceEntry)
            .where(ResourceEntry.pseudonym == str(pseudonym))
            .where(ResourceEntry.resource_type.ilike(resource_type))
        )

        return self.db_session.execute(stmt).scalars().all()  # type: ignore

    def find_by_resource(
        self, resource_type: str, resource_id: str, version: int
    ) -> ResourceEntry | None:
        stmt = (
            select(ResourceEntry)
            .where(ResourceEntry.resource_type.ilike(resource_type))
            .where(ResourceEntry.resource_id.ilike(resource_id))
            .limit(1)
        )

        if version == 0:
            # Get latest version
            stmt = stmt.order_by(ResourceEntry.version.desc())
        else:
            stmt = stmt.where(ResourceEntry.version == version)

        return self.db_session.execute(stmt).scalars().first()  # type: ignore

    def delete_by_resource(self, resource_type: str, resource_id: str) -> None:
        stmt = (
            update(ResourceEntry)
            .where(ResourceEntry.resource_type.ilike(resource_type))
            .where(ResourceEntry.resource_id.ilike(resource_id))
            .values(deleted=True)
        )

        self.db_session.execute(stmt)
        self.db_session.commit()

    def upsert(
        self,
        resource_type: str,
        resource_id: str,
        data: dict[str, Any],
        pseudonym: Pseudonym | None,
    ) -> ResourceEntry | None:
        with self.db_session.begin():
            # Create a new resource entry instance, assume version is 1
            entry = ResourceEntry(
                id=uuid.uuid4(),
                pseudonym=uuid.UUID(str(pseudonym)) if pseudonym else None,
                resource_type=resource_type,
                resource_id=resource_id,
                resource=data,
                version=1,
                created_dt=datetime.now(),
                deleted=False,
            )

            if "postgresql" in self.db_session.get_dialect():
                subquery = (
                    self.db_session.query(
                        func.coalesce(func.max(ResourceEntry.version), 0) + 1
                    ).filter(
                        ResourceEntry.resource_id == resource_id
                        and ResourceEntry.resource_type == resource_type
                    )
                ).scalar_subquery()

                from sqlalchemy.dialects.postgresql import insert

                insert_stmt = (
                    insert(ResourceEntry)
                    .values(
                        id=entry.id,
                        pseudonym=entry.pseudonym,
                        resource_type=entry.resource_type,
                        resource_id=entry.resource_id,
                        resource=entry.resource,
                        version=entry.version,
                        created_dt=entry.created_dt,
                        deleted=entry.deleted,
                    )
                    .on_conflict_do_update(
                        constraint="resource_type_id", set_={"version": subquery}
                    )
                )
                result = self.db_session.scalars(
                    insert_stmt.returning(ResourceEntry),
                    execution_options={"populate_existing": True},
                )
                return result.first()  # type: ignore

            if "sqlite" in self.db_session.get_dialect():
                # Sqlite does not support on conflict do update, so we need to manually check the version
                stmt = (
                    select(func.max(ResourceEntry.version))
                    .where(ResourceEntry.resource_type.ilike(resource_type))
                    .where(ResourceEntry.resource_id.ilike(resource_id))
                )
                result = self.db_session.execute(stmt)
                max_version = result.scalar()
                entry.version = (max_version or 0) + 1

                self.db_session.add(entry)
                self.db_session.commit()

                return entry

            raise Exception("Unsupported database dialect")
