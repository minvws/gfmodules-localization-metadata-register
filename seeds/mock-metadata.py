import json
import os
import random
from datetime import datetime, date
from typing import Any

import requests
from faker import Faker
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.fhirtypes import ImagingStudySeriesType
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries, ImagingStudySeriesInstance
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from requests.auth import HTTPBasicAuth

from app.config import get_config
from app.data import Pseudonym
from app.db.db import Database
from app.metadata.db.db_adapter import DbMetadataAdapter
from app.metadata.metadata_service import MetadataService

fake = Faker('nl_NL')

config = get_config()

db = Database(dsn=config.database.dsn, create_tables=config.database.create_tables)

metadata_service = MetadataService(DbMetadataAdapter(db))


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return str(json.JSONEncoder.default(self, obj))


def store(resource_type: str, resource_id: str, resource: Resource, pseudonym: Pseudonym):
    _dict = json.loads(json.dumps(resource.dict(), cls=CustomJSONEncoder))
    entry = metadata_service.update(resource_type, resource_id, _dict, pseudonym)
    if entry is None:
        raise Exception("Failed to store resource")


def generate_mocks(pseudonym):
    path = f"mocks/{pseudonym}"
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    patient = generate_patient()
    patient_id = patient.identifier[0].value
    with open(f"{path}/patient-{patient_id}.json", "w") as f:
        f.write(json.dumps(patient.dict(), indent=4, cls=CustomJSONEncoder))
    store("Patient", patient_id, patient, pseudonym)


    org = generate_organization()
    org_id = org.identifier[0].value
    with open(f"{path}/org-{org_id}.json", "w") as f:
        f.write(json.dumps(org.dict(), indent=4, cls=CustomJSONEncoder))
    store("Organization", org_id, org, pseudonym)

    # Generate 10 practitioners
    practitioners = []
    for _ in range(10):
        practitioner = generate_practitioner()
        practitioner_id = practitioner.identifier[0].value
        with open(f"{path}/practitioner-{practitioner_id}.json", "w") as f:
            f.write(json.dumps(practitioner.dict(), indent=4, cls=CustomJSONEncoder))
        practitioners.append(practitioner)
        store("Practitioner", practitioner_id, practitioner, pseudonym)

    for _ in range(fake.random_number(digits=1) + 1):
        study = generate_imagestudy(patient, org, practitioners)
        study_id = study.identifier[0].value
        with open(f"{path}/imagingstudy-{study_id}.json", "w") as f:
            f.write(json.dumps(study.dict(), indent=4, cls=CustomJSONEncoder))
        store("ImagingStudy", study_id, study, pseudonym)


def generate_first_names(gender: str) -> list[str]:
    number_of_names = random.choices(
        population=[1, 2, 3, 4],
        weights=[0.7, 0.2, 0.07, 0.03],  # Adjust weights according to your preference
        k=1
    )[0]

    if gender == "male":
        first_names = [fake.first_name_male() for _ in range(number_of_names)]
    elif gender == "female":
        first_names = [fake.first_name_female() for _ in range(number_of_names)]
    else:
        first_names = [fake.first_name_nonbinary() for _ in range(number_of_names)]

    return first_names


def generate_patient():
    uuid = fake.uuid4()
    gender = fake.random_element(elements=("male", "female", "other", "unknown"));

    patient = Patient(
        id=uuid,
        identifier=[Identifier(
            system="http://example.org/patient",
            value=uuid
        )],
        active=True,
        address=[Address(
            use='home',
            line=[fake.street_address()],
            city=fake.city(),
            postalCode=fake.postcode(),
            country='Netherlands'
        )],
        birthDate=fake.date_of_birth(),
        gender=gender,
        name=[HumanName(
            family=fake.last_name(),
            given=generate_first_names(gender),
        )]
    )

    if fake.random_number(digits=1) <= 2:
        patient.deceasedDateTime = fake.past_date()

    return patient


def generate_practitioner():
    uuid = fake.uuid4()

    practitioner = Practitioner(
        id=uuid,
        identifier=[Identifier(
            system="http://example.org/practitioner",
            value=uuid
        )],
        active=True,
        address=[Address(
            use='work',
            line=[fake.street_address()],
            city=fake.city(),
            postalCode=fake.postcode(),
            country='Netherlands'
        )],
        birthDate=fake.date_of_birth(),
    )

    return practitioner


def generate_imagestudy(patient: Patient, org: Organization, practitioners: list[Practitioner]):
    uuid = fake.uuid4()

    patient_id = patient.identifier[0].value
    org_id = org.identifier[0].value

    series_count = fake.random_number(digits=1) + 1

    study = ImagingStudy(
        id=uuid,
        identifier=[Identifier(
            system="http://example.org/study",
            value=uuid
        )],
        subject=Reference(
            reference=f"Patient/{patient_id}"
        ),
        status=fake.random_element(elements=("registered", "available", "cancelled", "entered-in-error")),
        started=fake.date_time_this_decade(),
        numberOfSeries=series_count,
        series=[]
    )

    for idx in range(series_count):
        practitioner = fake.random_element(elements=practitioners)
        practitioner_id = practitioner.identifier[0].value

        study.series.append(ImagingStudySeriesType(
            uid=fake.uuid4(),
            number=idx,
            started=fake.date_time_this_decade(),
            modality=CodeableConcept(
                coding=[Coding(
                    system="http://example.org/modality",
                    code=fake.random_element(elements=("CT", "MR", "US", "DX")),
                    display=fake.random_element(elements=("Computed Tomography", "Magnetic Resonance", "Ultrasound", "Digital Radiography"))
                )]
            ),
            performer=[
                {
                    "actor": Reference(
                        reference=f"Practitioner/{practitioner_id}",
                        type="Practitioner"
                    ),
                },
                {
                    "actor": Reference(
                        reference=f"Organization/{org_id}",
                        type="Organization"
                    ),
                }
            ],
            bodySite=CodeableReference(
                concept=CodeableConcept(
                    coding=[Coding(
                        system="http://example.org/body-site",
                        code=fake.random_element(elements=("head", "chest", "abdomen", "pelvis")),
                        display=fake.random_element(elements=("Head", "Chest", "Abdomen", "Pelvis"))
                    )]
                )
            ),
            instance=[ImagingStudySeriesInstance(
                uid=fake.uuid4(),
                number=idx,
                sopClass=Coding(
                    system="http://example.org/sop-class",
                    code=fake.random_element(elements=("CT", "MR", "US", "DX")),
                    display=fake.random_element(
                    elements=("Computed Tomography", "Magnetic Resonance", "Ultrasound", "Digital Radiography"))
                ),
                title=fake.sentence(),
            )]
        ))

    return study


def generate_organization():
    uuid = fake.uuid4()

    org = Organization(
        id=uuid,
        identifier=[Identifier(
            system="http://example.org/org",
            value=uuid
        )],
        active=True,
        type=[CodeableConcept(
            coding=[Coding(
                system="http://example.org/org-type",
                code=fake.random_element(elements=("hospital", "clinic", "pharmacy", "lab")),
                display=fake.random_element(elements=("Hospital", "Clinic", "Pharmacy", "Lab"))
            )]
        )],
        name=fake.company(),
    )

    return org


if __name__ == '__main__':
    generate_mocks(Pseudonym("bbf54282-3d58-4bed-b27b-dd4e1b85ec08"))
