# Business rules ImageStudy
#   - Patient subject resource must be present
#   - Observation resource must be present
#   - ImagingStudy must have a reference to a Patient
#   - Series must have references to both an organisation and a physician
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.resource import Resource

from app.metadata.validators.Validator import Validator


class ImagingStudyValidator(Validator):

    def validate(self, obj: Resource) -> None:
        if not isinstance(obj, ImagingStudy):
            raise Exception("Resource is not an ImagingStudy")

        if obj.subject is None:
            raise Exception("Subject resource must be present")

        if obj.subject.type != 'Patient':  # type: ignore
            raise Exception("Subject resource type is not Patient")

        pass