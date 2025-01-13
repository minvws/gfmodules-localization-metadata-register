from collections.abc import Sequence
from typing import Final

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.medication import Medication, MedicationIngredient
from fhir.resources.R4B.narrative import Narrative
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.ratio import Ratio

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    fake,
    generate_coding,
    generate_identification,
    generate_reference,
    write_and_store,
)

STATUS: Final[tuple[str, ...]] = ("active", "inactive", "entered-in-error")
MEDICATION_FORMS: Final[tuple[str, ...]] = (
    "Capsule",
    "Tablet",
    "Syrup",
    "Drops",
    "Injection",
    "Inhaler",
    "Patch",
    "Suppository",
    "Ointment",
    "Cream",
    "Gel",
    "Lotion",
    "Shampoo",
    "Solution",
    "Suspension",
    "Spray",
    "Lozenge",
    "Powder",
    "Granules",
    "Aerosol",
    "Mouthwash",
    "Paste",
    "Gargle",
    "Dressing",
    "Wash",
    "Oil",
    "Emulsion",
    "Foam",
    "Jelly",
    "Pessary",
    "Douche",
)
INGREDIENTS: Final[tuple[str, ...]] = (
    "Acetaminophen",
    "Amoxicillin",
    "Baclofen",
    "Caffeine",
    "Dextromethorphan",
    "Ephedrine",
    "Fentanyl",
    "Guaifenesin",
    "Hydrocodone",
    "Ibuprofen",
    "Jasmine",
    "Ketamine",
    "Lorazepam",
    "Morphine",
    "Naproxen",
    "Oxycodone",
    "Phenylephrine",
    "Quinine",
    "Ranitidine",
    "Sildenafil",
    "Tadalafil",
    "Ursodiol",
    "Vardenafil",
    "Warfarin",
    "Xylometazoline",
    "Yohimbine",
    "Zolpidem",
)
MEDICATION_CODES: Final[tuple[str, ...]] = (
    "Deoxycortone",
    "Ephedrine",
    "Fentanyl",
    "Guaifenesin",
    "Hydrocodone",
    "Ibuprofen",
    "Jasmine",
    "Ketamine",
    "Lorazepam",
    "Morphine",
    "Naproxen",
    "Oxycodone",
    "Phenylephrine",
    "Quinine",
    "Ranitidine",
    "Sildenafil",
    "Tadalafil",
    "Ursodiol",
    "Vardenafil",
    "Warfarin",
    "Xylometazoline",
    "Yohimbine",
    "Zolpidem",
)


def generate_ingredient() -> MedicationIngredient:
    return MedicationIngredient(
        isActive=fake.boolean(chance_of_getting_true=60),
        itemCodeableConcept=CodeableConcept(
            coding=[generate_coding("rxnorm", INGREDIENTS)]
        ),
        strength=generate_ratio(),
    )


def generate_ratio() -> Ratio:
    return Ratio(
        numerator=generate_quantity(),
        denominator=generate_quantity(),
    )


def generate_quantity() -> Quantity:
    unit = fake.random_element(elements=("mg", "mL", "g", "units"))
    return Quantity(
        code=unit,
        system="http://unitsofmeasure.org",
        value=fake.random_number(digits=3),
        unit=unit,
        comparator=None,
    )


def generate_medication(manufacturer: Organization) -> Medication:
    return Medication(
        **generate_identification("Medication"),
        code=CodeableConcept.construct(
            coding=[generate_coding("rxnorm", MEDICATION_CODES)]
        ),
        status=fake.random_element(elements=STATUS),
        manufacturer=generate_reference(
            manufacturer, manufacturer.name or fake.company()
        ),
        form=CodeableConcept.construct(
            coding=[generate_coding("DrugForm", MEDICATION_FORMS)]
        ),
        amount=generate_ratio(),
        ingredient=[
            generate_ingredient() for _ in range(1, fake.random.randrange(3, 5))
        ],
    )


def mock_medication(
    pseudonym: Pseudonym,
    organizations: Sequence[Organization],
) -> list[Medication]:
    return [
        write_and_store(
            generate_medication(fake.random_element(elements=organizations)), pseudonym
        )
        for _ in range(8)
    ]
