from collections.abc import Sequence
import random

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.dosage import Dosage, DosageDoseAndRate
from fhir.resources.R4B.fhirtypes import QuantityType
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.medicationstatement import MedicationStatement
from fhir.resources.R4B.patient import Patient
from typing_extensions import Final

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    displayname,
    fake,
    generate_coding,
    generate_identification,
    generate_period,
    generate_reference,
    write_and_store,
    URI_EXAMPLE,
)

STATUS: Final[tuple[str, ...]] = ("active", "inactive", "entered-in-error")
DOSAGE_ROUTE: Final[tuple[str, ...]] = ("Oral", "Vaginal", "Topical", "Nasal")
DOSAGE_TYPE: Final[tuple[str, ...]] = ("Calculated", "Ordered")
UNITS: Final[tuple[str, ...]] = ("mg", "mg/dL", "mmol/kg", "mmol/mL")


def generate_dose_and_rate() -> DosageDoseAndRate:
    return DosageDoseAndRate.construct(
        type=CodeableConcept.construct(coding=[generate_coding("dose-rate-type", DOSAGE_TYPE)]),
        doseQuantity=QuantityType(
            value=random.uniform(1, 10),
            system=f"{URI_EXAMPLE}/units-of-mesure.org",
            unit=fake.random_element(elements=UNITS),
            code=random.randint(100000, 999999),
        ),
    )


def generate_dosage() -> Dosage:
    return Dosage.construct(
        doseAndRate=[generate_dose_and_rate()],
        route=CodeableConcept.construct(coding=[generate_coding("route-codes", DOSAGE_ROUTE)]),
    )


def generate_medication_statement(medication: Medication, subject: Patient) -> MedicationStatement:
    return MedicationStatement.construct(
        **generate_identification("MedicationStatement"),
        status=fake.random_element(elements=STATUS),
        medicationReference=generate_reference(medication, str(medication.text) if medication.text else None),
        subject=generate_reference(subject, displayname(subject.name[0])),
        effectivePeriod=generate_period(),
        reasonCode=[
            CodeableConcept.construct(
                coding=[
                    generate_coding(
                        "reason",
                        ("Homoiothermia", "Alcohol user", "Sycosis", "Allotype"),
                    )
                ]
            )
        ],
        dosage=[generate_dosage()],
    )


def mock_medication_statemnt(pseudonym: Pseudonym, patient: Patient, medications: Sequence[Medication]) -> None:
    for medication in medications:
        write_and_store(
            generate_medication_statement(medication, patient),
            pseudonym,
        )
