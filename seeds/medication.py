from typing import Final
from uuid import UUID

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.ingredient import Ingredient
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.ratio import Ratio

from seeds.utils import fake, generate_coding, generate_identifier, generate_reference

STATUS: Final[tuple[str, ...]] = ("active", "inactive")
MEDICATION_FORMS: Final[tuple[str, ...]] = ("Capsule", "Tablet", "Syrup")


def generate_ingredient() -> Ingredient:
    return Ingredient.construct()


def generate_ratio() -> Ratio:
    return Ratio.construct()


def generate_medication(manufacturer: Organization) -> Medication:
    id = fake.uuid4()

    return Medication.construct(
        id=id,
        identifier=[generate_identifier("Medication", id)],
        code=CodeableConcept.construct(coding=[generate_coding("rxnorm")]),
        status=fake.random_element(elements=STATUS),
        manufacturer=generate_reference(
            "Organization", UUID(manufacturer.id), manufacturer.name
        ),
        form=CodeableConcept.construct(
            coding=[generate_coding("DrugForm", MEDICATION_FORMS)]
        ),
    )
