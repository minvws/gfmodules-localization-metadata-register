import logging
from typing import cast

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from fhir.resources.resource import Resource

from app.data import DataDomain, Pseudonym, ProviderID
from app.db.db import Database
from app.db.models import FhirReference, FhirResource
from app.db.repository.reference_entry import FhirReferenceRepository
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

    if res.data['resourceType'] == 'Patient':
        return Patient.parse_obj(res.data)
    elif res.data['resourceType'] == 'ImagingStudy':
        return ImagingStudy.parse_obj(res.data)
    elif res.data['resourceType'] == 'Observation':
        return Observation.parse_obj(res.data)
    else:
        return None


class DbMetadataAdapter(MetadataAdapter):
    def __init__(self, db: Database):
        self.db = db

    def search(self, provider_id: ProviderID | None, data_domain: DataDomain, pseudonym: Pseudonym) -> Bundle | None:
        """
        Search for metadata for a specific id and service. Note that the provider_id is not used and is deprecated. It will
        be removed in a future version.
        """
        session = self.db.get_db_session()
        ref_repository = self.get_fhir_reference_repository(session)
        if not ref_repository:
            return None
        resource_repository = self.get_fhir_resource_repository(session)
        if not resource_repository:
            return None

        # Find entries for this given pseudonym
        entries = ref_repository.find_by_pseudonym(pseudonym)
        if not entries:
            return None

        timeline_entries = []
        for entry in entries:
            # Each entry found for the pseudonym is a timeline entry
            timeline_entry = Bundle(
                resource_type='Bundle',
                type='timeline',
                entry=[]
            )

            # Each timeline entry has one or more references to the actual data (patient info, image study, observations etc)
            for reference in entry.references:
                res = resource_repository.find_by_resource(reference['resource_type'], reference['resource_id'])
                if res is not None:
                    fhir_res = convert_resource_to_fhir(res)
                    if fhir_res is not None:
                        timeline_entry.entry.append(BundleEntry(
                            resource=fhir_res,
                        ))

            timeline_entries.append(BundleEntry(
                resource=timeline_entry
            ))

        # Return a bundle with all timeline entries. These are custom bundles that do not map to any FHIR structure
        entry = Bundle(
            resource_type='Bundle',
            type='timeline',
            entry=timeline_entries
        )

        return entry

    @staticmethod
    def get_fhir_reference_repository(session: DbSession) -> FhirReferenceRepository:
        return cast(
            FhirReferenceRepository,
            session.get_repository(FhirReference)
        )

    @staticmethod
    def get_fhir_resource_repository(session: DbSession) -> FhirResourceRepository:
        return cast(
            FhirResourceRepository,
            session.get_repository(FhirResource)
        )
