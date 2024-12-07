from collections.abc import Sequence
from typing import Final

from fhir.resources.R4B.imagingstudy import (
    ImagingStudy,
    ImagingStudySeries,
    ImagingStudySeriesInstance,
)
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.practitioner import Practitioner

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    displayname,
    fake,
    generate_coding,
    generate_identification,
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


def _imaging_study_series(practitioner: Practitioner, organization: Organization, idx: int) -> ImagingStudySeries:
    return ImagingStudySeries.construct(
        uid=fake.uuid4(),
        number=idx,
        started=fake.date_time_this_decade(),
        modality=generate_coding("modality", IMAGING_CODES),
        performer=[
            {
                "actor": generate_reference(practitioner, displayname(practitioner.name[0])),
            },
            {"actor": generate_reference(organization, organization.name or fake.company())},
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
    practitioners: Sequence[Practitioner],
):
    series_count = fake.random_number(digits=1) + 1

    return ImagingStudy.construct(
        **generate_identification("study"),
        subject=generate_reference(patient, displayname(patient.name[0])),
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


def mock_image_study(
    pseudonym: Pseudonym,
    organizations: Sequence[Organization],
    practitioners: Sequence[Practitioner],
    patient: Patient,
):
    for _ in range(fake.random_number(digits=1) + 2):
        write_and_store(
            generate_imagestudy(
                patient,
                fake.random_element(elements=organizations),
                practitioners,
            ),
            pseudonym,
        )
