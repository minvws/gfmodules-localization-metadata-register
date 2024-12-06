from typing import Any, Protocol, Sequence

from app.data import Pseudonym
from app.db.models import ResourceEntry
from app.metadata.fhir import convert_resource_to_fhir
from app.metadata.validators.ImagingStudy import ImagingStudyValidator
from app.metadata.validators.medication import MedicationValidator
from app.metadata.validators.medication_statement import MedicationStatementValidator
from app.metadata.validators.Patient import PatientValidator
from app.metadata.validators.Validator import (
    InvalidResourceError,
    ValidationError,
    Validator,
)


class MetadataAdapter(Protocol):
    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[ResourceEntry]: ...

    def search(self, resource_type: str, resource_id: str, version: int) -> ResourceEntry | None: ...

    def delete(self, resource_type: str, resource_id: str) -> None: ...

    def update(
        self,
        resource_type: str,
        resource_id: str,
        data: dict[str, Any],
        pseudonym: Pseudonym | None,
    ) -> ResourceEntry | None: ...


def create_validator(resource_type: str) -> Validator | None:
    match resource_type:
        case "ImagingStudy":
            return ImagingStudyValidator()
        case "Patient":
            return PatientValidator()
        case "Medication":
            return MedicationValidator()
        case _:
            return None


def validate_resource(resource_type: str, resource_id: str, data: dict[str, Any]) -> None:
    if data is None:
        raise ValidationError()

    if "resourceType" not in data:
        raise ValidationError("resourceType is required in the resource data")
    if data["resourceType"].lower() != resource_type.lower():
        raise InvalidResourceError("resource type does not match the resource type in the URL")

    if "id" not in data:
        raise ValidationError("id is required in the resource data")
    if data["id"].lower() != resource_id.lower():
        raise ValidationError("id in the resource data does not match the resource id in the URL")

    fhir_resource = convert_resource_to_fhir(data)
    if fhir_resource is None:
        raise InvalidResourceError("Resource is invalid")

    validator = create_validator(resource_type)
    if validator:
        validator.validate(fhir_resource)


class MetadataService:
    def __init__(self, adapter: MetadataAdapter):
        self.adapter = adapter

    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[ResourceEntry]:
        return self.adapter.search_by_pseudonym(pseudonym, resource_type)

    def search(self, resource_type: str, resource_id: str, version: int) -> ResourceEntry | None:
        return self.adapter.search(resource_type, resource_id, version)

    def delete(self, resource_type: str, resource_id: str) -> None:
        return self.adapter.delete(resource_type, resource_id)

    def update(
        self,
        resource_type: str,
        resource_id: str,
        data: dict[str, Any],
        pseudonym: Pseudonym | None,
    ) -> ResourceEntry | None:
        validate_resource(resource_type, resource_id, data)
        return self.adapter.update(resource_type, resource_id, data, pseudonym)
