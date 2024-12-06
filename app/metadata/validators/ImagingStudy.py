# Business rules ImageStudy
#   - Patient subject resource must be present
#   - Series must have references to both an organisation and a physician
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries
from fhir.resources.resource import Resource

from app.metadata.validators.Validator import Validator


class ImagingStudyValidator(Validator):
    def validate(self, obj: Resource) -> None:
        if not isinstance(obj, ImagingStudy):
            raise Exception("Resource is not an ImagingStudy")

        if obj.subject is None:
            raise Exception("Subject resource must be present")

        if obj.started is None:
            raise Exception("Started date must be present")

        for series_entry in obj.series:
            if not isinstance(series_entry, ImagingStudySeries):
                raise Exception("Instance found in series is not an ImagingStudySeries")

            if series_entry.started is None:
                raise Exception("Started date must be present in each series")

            if series_entry.performer is None:
                raise Exception("Performer must be present in each series")

            org_found = False
            physician_found = False
            for performer in series_entry.performer:
                if performer.actor.type == "Organization":
                    org_found = True
                if performer.actor.type == "Practitioner":
                    physician_found = True

            if not org_found:
                raise Exception("Performer must have an organization in each series")
            if not physician_found:
                raise Exception("Performer must have a physician in each series")

        pass
