from fhir.resources.R4B.resource import Resource

from app.metadata.validators.Validator import Validator


class PatientValidator(Validator):
    @override
    def validate(self, obj: Resource) -> None:
        pass
