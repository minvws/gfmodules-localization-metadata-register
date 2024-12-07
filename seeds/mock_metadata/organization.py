from typing import Final
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.organization import Organization

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    generate_coding,
    generate_identification,
    write_and_store,
)

ORGANIZATION_TYPES: Final[tuple[str, ...]] = ("Hospital", "Clinic", "Pharmacy", "Lab")
COMPONENT: Final[str] = "org"

ORGANIZATION_NAMES: Final[tuple[str, ...]] = (
    "De Ziekenboeg",
    "Huisartsenpost Bloedspoed",
    "Ziekthuis",
)


def generate_organization(name: str) -> Organization:
    return Organization.construct(
        **generate_identification(COMPONENT),
        active=True,
        type=[CodeableConcept.construct(coding=[generate_coding(f"{COMPONENT}-type", ORGANIZATION_TYPES)])],
        name=name,
    )


def mock_organization(pseudonym: Pseudonym) -> list[Organization]:
    return [write_and_store(generate_organization(name), pseudonym) for name in ORGANIZATION_NAMES]
