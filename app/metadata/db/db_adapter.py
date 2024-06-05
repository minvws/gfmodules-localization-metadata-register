import logging
from typing import cast, Sequence, Tuple, Any

from app.data import Pseudonym
from app.db.db import Database
from app.db.models import ResourceEntry
from app.db.repository.resource_entry import ResourceEntryRepository
from app.db.session import DbSession
from app.metadata.metadata_service import MetadataAdapter

logger = logging.getLogger(__name__)


def sanitize(resource_type: str, resource_id: str) -> Tuple[str, str]:
    # Remove any % and ? characters from the resource type and id
    resource_type = resource_type.replace('%', '')
    resource_type = resource_type.replace('?', '')
    resource_id = resource_id.replace('%', '')
    resource_id = resource_id.replace('?', '')

    return resource_type, resource_id


class DbMetadataAdapter(MetadataAdapter):
    def __init__(self, db: Database):
        self.db = db

    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[ResourceEntry]:
        """
        Search for metadata for a pseudonym
        """
        session = self.db.get_db_session()

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return []

        return resource_repository.find_by_pseudonym(pseudonym, resource_type)

    def search(self, resource_type: str, resource_id: str, version: int) -> ResourceEntry | None:
        """
        Search for metadata for a resource
        """
        session = self.db.get_db_session()

        (resource_type, resource_id) = sanitize(resource_type, resource_id)

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return None

        return resource_repository.find_by_resource(resource_type, resource_id, version)

    def delete(self, resource_type: str, resource_id: str) -> None:
        """
        Delete metadata for a resource
        """
        session = self.db.get_db_session()

        (resource_type, resource_id) = sanitize(resource_type, resource_id)

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return None

        resource_repository.delete_by_resource(resource_type, resource_id)

    def update(self, resource_type: str, resource_id: str, data: dict[str, Any], pseudonym: Pseudonym) -> ResourceEntry | None:
        """
        Update metadata for a resource
        """
        session = self.db.get_db_session()

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return None

        return resource_repository.upsert(resource_type, resource_id, data, pseudonym)

    @staticmethod
    def get_fhir_resource_repository(session: DbSession) -> ResourceEntryRepository:
        return cast(
            ResourceEntryRepository,
            session.get_repository(ResourceEntry)
        )
