
from sqlalchemy import select

from app.db.repository import RepositoryBase
from app.db.decorator import repository
from app.db.models import FhirResource


@repository(FhirResource)
class FhirResourceRepository(RepositoryBase):
    def find_by_resource(self, resource_type: str, resource_id: str) -> FhirResource | None:
        stmt = (select(FhirResource)
                .where(FhirResource.resource_type == resource_type)
                .where(FhirResource.resource_id == resource_id))

        return self.session.execute(stmt).scalars().first()

