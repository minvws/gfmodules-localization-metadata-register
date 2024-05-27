from typing import Sequence

from sqlalchemy import select

from app.data import Pseudonym
from app.db.repository import RepositoryBase
from app.db.decorator import repository
from app.db.models import FhirReference


@repository(FhirReference)
class FhirReferenceRepository(RepositoryBase):
    def find_by_pseudonym(self, pseudonym: Pseudonym) -> Sequence[FhirReference] | None:
        stmt = select(FhirReference).where(FhirReference.pseudonym == pseudonym)
        return self.session.execute(stmt).scalars().all()
