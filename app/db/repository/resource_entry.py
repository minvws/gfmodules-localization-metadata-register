
from sqlalchemy import select, delete
from typing import Sequence

from app.data import Pseudonym
from app.db.repository import RepositoryBase
from app.db.decorator import repository
from app.db.models import FhirResource


@repository(FhirResource)
class FhirResourceRepository(RepositoryBase):
    def find_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[FhirResource]:
        stmt = (select(FhirResource)
                .where(FhirResource.pseudonym == str(pseudonym))
                .where(FhirResource.resource_type.ilike(resource_type)))

        return self.session.execute(stmt).scalars().all()

    def find_by_resource(self, resource_type: str, resource_id: str) -> FhirResource | None:
        stmt = (select(FhirResource)
                .where(FhirResource.resource_type.ilike(resource_type))
                .where(FhirResource.resource_id.ilike(resource_id)))

        return self.session.execute(stmt).scalars().first()

    def delete_by_resource(self, resource_type: str, resource_id: str) -> None:
        stmt = (delete(FhirResource)
                .where(FhirResource.resource_type.ilike(resource_type))
                .where(FhirResource.resource_id.ilike(resource_id)))

        self.session.execute(stmt)
        self.session.commit()