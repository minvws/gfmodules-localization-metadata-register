from functools import partial
from typing import Final
from uuid import UUID

from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.imagingstudy import (
    ImagingStudy,
    ImagingStudySeries,
    ImagingStudySeriesInstance,
)
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.practitioner import Practitioner

from app.data import Pseudonym
from seeds.organization import generate_organization
from seeds.person import generate_patient, generate_practitioner
from seeds.utils import (
    fake,
    generate_coding,
    generate_identifier,
    generate_reference,
    write_and_store,
)

STATUS: Final[tuple[str, ...]] = (
    "registered",
    "available",
    "cancelled",
    "entered-in-error",
)
IMAGING_CODES: Final[tuple[str, ...]] = (
    "Computed Tomography",
    "Magnetic Resonance",
    "Ultrasound",
    "Digital Radiography",
)
BODY_PARTS: Final[tuple[str, ...]] = (
    "Hoofd",
    "Borst",
    "Buikholte",
    "Bekken",
)
ORGANIZATION_NAMES: Final[tuple[str, ...]] = (
    "De Ziekenboeg",
    "Huisartsenpost Bloedspoed",
    "Ziekthuis",
)
PRACTICIONS: Final[tuple[tuple[str, str], ...]] = (
    ("Dokter", "Bibber"),
    ("Zuster", "Bloedwijn"),
    ("Oogarts", "Appel"),
    ("Radioloog", "Straal"),
)


def _displayname(name: HumanName):
    return f"{name.given[0]} {name.family}"


def _imaging_study_series(
    practitioner: Practitioner, organization: Organization, idx: int
) -> ImagingStudySeries:
    return ImagingStudySeries.construct(
        uid=fake.uuid4(),
        number=idx,
        started=fake.date_time_this_decade(),
        modality=generate_coding("modality", IMAGING_CODES),
        performer=[
            {
                "actor": generate_reference(
                    "Practitioner",
                    UUID(practitioner.id),
                    _displayname(practitioner.name[0]),
                ),
            },
            {
                "actor": generate_reference(
                    "Organization", UUID(organization.id), organization.name
                )
            },
        ],
        body_site=generate_coding("body-site", BODY_PARTS),
        instance=[
            ImagingStudySeriesInstance.construct(
                uid=fake.uuid4(),
                number=idx,
                sopClass=generate_coding("sop-class", IMAGING_CODES),
                title=fake.sentence(),
            )
        ],
    )


def generate_imagestudy(
    patient: Patient,
    organization: Organization,
    practitioners: list[Practitioner],
):
    uuid = fake.uuid4()
    series_count = fake.random_number(digits=1) + 1

    return ImagingStudy.construct(
        id=uuid,
        identifier=[generate_identifier("study", uuid)],
        subject=generate_reference(
            "Patient", UUID(patient.id), _displayname(patient.name[0])
        ),
        status=fake.random_element(elements=STATUS),
        started=fake.date_time_this_decade(),
        numberOfSeries=series_count,
        series=[
            _imaging_study_series(
                fake.random_element(elements=practitioners),
                organization,
                idx,
            )
            for idx in range(series_count)
        ],
    )


def mock_image_study(pseudonym: Pseudonym):
    _write_and_store = partial(write_and_store, pseudonym=pseudonym)

    organizations = [
        _write_and_store(resource=generate_organization(name))
        for name in ORGANIZATION_NAMES
    ]

    # Generate 10 practitioners
    practitioners = [
        _write_and_store(resource=generate_practitioner(*name)) for name in PRACTICIONS
    ]

    for _ in range(fake.random_number(digits=1) + 2):
        _write_and_store(
            resource=generate_imagestudy(
                _write_and_store(resource=generate_patient()),
                fake.random_element(elements=organizations),
                practitioners,
            )
        )
