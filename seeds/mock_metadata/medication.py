from collections.abc import Sequence
from typing import Final

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.ingredient import Ingredient
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.ratio import Ratio

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    fake,
    generate_coding,
    generate_identification,
    generate_reference,
    write_and_store,
)

STATUS: Final[tuple[str, ...]] = ("active", "inactive")
MEDICATION_FORMS: Final[tuple[str, ...]] = ("Capsule", "Tablet", "Syrup")


def generate_ingredient() -> Ingredient:
    return Ingredient.construct()


def generate_ratio() -> Ratio:
    return Ratio.construct()


def generate_medication(manufacturer: Organization) -> Medication:
    return Medication.construct(
        **generate_identification("Medication"),
        code=CodeableConcept.construct(coding=[generate_coding("rxnorm")]),
        status=fake.random_element(elements=STATUS),
        manufacturer=generate_reference(manufacturer, manufacturer.name or fake.company()),
        form=CodeableConcept.construct(coding=[generate_coding("DrugForm", MEDICATION_FORMS)]),
    )


def mock_medication(
    pseudonym: Pseudonym,
    organizations: Sequence[Organization],
) -> list[Medication]:
    return [
        write_and_store(generate_medication(fake.random_element(elements=organizations)), pseudonym)
        for _ in range(fake.random_number(digits=1) + 2)
    ]
