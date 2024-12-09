from fhir.resources.resource import Resource

from app.metadata.validators.Validator import Validator


class PatientValidator(Validator):
    def validate(self, obj: Resource) -> None:
        pass
