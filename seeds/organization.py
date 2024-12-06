from typing import Final
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.organization import Organization

from seeds.utils import generate_coding, generate_identifier, fake

ORGANIZATION_TYPES: Final[tuple[str, ...]] = ("Hospital", "Clinic", "Pharmacy", "Lab")
COMPONENT: Final[str] = "org"


def generate_organization(name: str) -> Organization:
    uuid = fake.uuid4()

    return Organization.construct(
        id=uuid,
        identifier=[generate_identifier(COMPONENT, uuid)],
        active=True,
        type=[
            CodeableConcept.construct(
                coding=[generate_coding(f"{COMPONENT}-type", ORGANIZATION_TYPES)]
            )
        ],
        name=name,
    )
