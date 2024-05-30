import logging
from typing import cast, Sequence, Tuple

from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from fhir.resources.resource import Resource

from app.data import Pseudonym
from app.db.db import Database
from app.db.models import FhirResource
from app.db.repository.resource_entry import FhirResourceRepository
from app.db.session import DbSession
from app.metadata.metadata_service import MetadataAdapter

logger = logging.getLogger(__name__)


def convert_resource_to_fhir(res: FhirResource) -> Resource|None:
    """
    Convert a FhirResource (flat database entry) to a FHIR resource model. This is a simple mapping function, but
    we can't use the parse_obj method directly, as the resource type is not known at compile time.
    """
    if not res:
        return None

    if res.resource['resourceType'] == 'Patient':
        return Patient.parse_obj(res.resource)
    elif res.resource['resourceType'] == 'ImagingStudy':
        return ImagingStudy.parse_obj(res.resource)
    elif res.resource['resourceType'] == 'Observation':
        return Observation.parse_obj(res.resource)
    else:
        logger.error(f"Unknown resource type {res.resource['resourceType']}")
        return None


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

    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[Resource]:
        """
        Search for metadata for a pseudonym
        """
        session = self.db.get_db_session()

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return []

        resources = resource_repository.find_by_pseudonym(pseudonym, resource_type)
        result = []
        for r in resources:
            fhir_resource = convert_resource_to_fhir(r)
            if fhir_resource is not None:
                result.append(fhir_resource)

        return result

    def search(self, resource_type: str, resource_id: str) -> Resource | None:
        """
        Search for metadata for a resource
        """
        session = self.db.get_db_session()

        (resource_type, resource_id) = sanitize(resource_type, resource_id)

        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return None

        res = resource_repository.find_by_resource(resource_type, resource_id)
        if res is None:
            return None

        fhir_res = convert_resource_to_fhir(res)
        if fhir_res is None:
            return None

        return fhir_res

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


    @staticmethod
    def get_fhir_resource_repository(session: DbSession) -> FhirResourceRepository:
        return cast(
            FhirResourceRepository,
            session.get_repository(FhirResource)
        )
