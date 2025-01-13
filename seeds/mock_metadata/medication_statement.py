from collections.abc import Sequence
import random
from datetime import date

from fhir.resources.R4B.annotation import Annotation
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.dosage import Dosage, DosageDoseAndRate
from fhir.resources.R4B.fhirtypes import QuantityType, PeriodType
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.medicationstatement import MedicationStatement
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.reference import Reference
from typing_extensions import Final

from app.data import Pseudonym
from seeds.mock_metadata.utils import (
    displayname,
    fake,
    generate_coding,
    generate_identification,
    generate_reference,
    write_and_store,
    URI_EXAMPLE,
    _generate_period,
)

STATUS: Final[tuple[str, ...]] = (
    "active",
    "completed",
    "entered-in-error",
    "intended",
    "stopped",
    "on-hold",
    "unknown",
    "not-taken",
)
DOSAGE_ROUTE: Final[tuple[str, ...]] = (
    "Oral",
    "Sublingual",
    "Buccal",
    "Nasal",
    "Rectal",
    "Vaginal",
    "Ophthalmic",
    "Otic",
    "Topical",
    "Transdermal",
    "Intradermal",
    "Subcutaneous",
)
DOSAGE_TYPE: Final[tuple[str, ...]] = ("Calculated", "Ordered")
UNITS: Final[tuple[str, ...]] = ("mg", "mg/dL", "mmol/kg", "mmol/mL")
ADDITIONAL_INSTRUCTIONS: Final[tuple[str, ...]] = (
    "Take with food",
    "Take on an empty stomach",
    "Take with plenty of water",
    "Take with a full glass of water",
    "Take with a meal",
    "Take with a snack",
)
METHODS: Final[tuple[str, ...]] = (
    "Swallow",
    "Chew",
    "Dissolve",
    "Inhale",
    "Insert",
    "Inject",
)
SITE_CODES: Final[tuple[str, ...]] = (
    "Left arm",
    "Right arm",
    "Left leg",
    "Right leg",
    "Abdomen",
    "Back",
    "Chest",
    "Mouth",
    "Nose",
    "Ear",
    "Eye",
)
CATEGORY: Final[tuple[str, ...]] = (
    "Inpatient",
    "Outpatient",
    "Community",
    "Patient Specified",
)
REASON: Final[tuple[str, ...]] = (
    "Homoiothermia",
    "Alcohol user",
    "Sycosis",
    "Chronic fatigue syndrome",
    "Hemorrhage",
    "Hypertension",
    "Hypotension",
    "Hypoxemia",
    "Allotype",
)
STATUS_REASON: Final[tuple[str, ...]] = (
    "Not taken",
    "Patient decision",
    "Adverse reaction",
    "Drug interaction",
    "Incorrect dose",
    "Incorrect medication",
    "Incorrect timing",
    "Refused",
    "Stopped by prescriber",
    "Stopped by patient",
    "Stopped by system",
    "Unknown",
    "Other",
)
NOTES: Final[tuple[str, ...]] = (
    "Patient reports mild seasonal allergies; no history of asthma.",
    "Patient denies any history of heart conditions or diabetes.",
    "According to patient, they have not received a tetanus booster in the last decade.",
    "Patient reports experiencing migraines triggered by strong fragrances.",
    "Patient is lactose intolerant and avoids dairy products.",
)


def generate_dose_and_rate() -> DosageDoseAndRate:
    return DosageDoseAndRate.construct(
        type=CodeableConcept.construct(coding=[generate_coding("dose-rate-type", DOSAGE_TYPE)]),
        doseQuantity=QuantityType(
            value=random.uniform(1, 10),
            system=f"{URI_EXAMPLE}/units-of-measure.org",
            unit=fake.random_element(elements=UNITS),
            code=random.randint(100000, 999999),
        ),
    )


def generate_dosage() -> Dosage:
    return Dosage.construct(
        additionalInstruction=[
            CodeableConcept.construct(
                coding=[
                    generate_coding(
                        "additional-instructions",
                        ADDITIONAL_INSTRUCTIONS,
                    )
                ]
            )
        ],
        asNeededBoolean=fake.boolean(chance_of_getting_true=20),
        doseAndRate=[generate_dose_and_rate()],
        maxDosePerAdministration=QuantityType(
            value=random.uniform(1, 10),
            system=f"{URI_EXAMPLE}/units-of-measure.org",
            unit=fake.random_element(elements=UNITS),
            code=random.randint(100000, 999999),
        ),
        method=CodeableConcept.construct(
            coding=[
                generate_coding(
                    "dosage-method",
                    METHODS,
                )
            ]
        ),
        route=CodeableConcept.construct(coding=[generate_coding("route-codes", DOSAGE_ROUTE)]),
        sequence=random.randint(1, 4),
        site=CodeableConcept.construct(
            coding=[
                generate_coding(
                    "site-codes",
                    SITE_CODES,
                )
            ]
        ),
    )


def generate_information_source() -> Reference:
    source_type = fake.random_element(
        elements=(
            "Patient",
            "Practitioner",
            "PractitionerRole",
            "RelatedPerson",
            "Organization",
        )
    )
    return Reference.construct(
        reference=f"{URI_EXAMPLE}/{source_type}/{fake.uuid4()}",
        display=fake.company() if source_type == "Organization" else fake.name(),
        type=source_type,
    )


def generate_medication_statement(
    medication: Medication,
    subject: Patient,
    start_date: date | None = None,
    end_date: date | None = None,
) -> MedicationStatement:
    return MedicationStatement.construct(
        basedOn=None,  # Not implemented
        category=CodeableConcept.construct(
            coding=[
                generate_coding(
                    "category",
                    CATEGORY,
                )
            ]
        ),
        context=None,  # Not implemented
        dateAsserted=fake.past_datetime(),
        derivedFrom=None,  # Not implemented
        dosage=[generate_dosage()],
        effectivePeriod=PeriodType(**_generate_period(start_date, end_date)),
        **generate_identification("MedicationStatement"),
        informationSource=generate_information_source(),
        medicationReference=generate_reference(medication, str(medication.code.coding[0].display)),
        note=[
            Annotation.construct(
                text=fake.random_element(
                    elements=NOTES,
                )
            )
        ],
        partOf=None,  # Not implemented
        reasonCode=[
            CodeableConcept.construct(
                coding=[
                    generate_coding(
                        "reason",
                        REASON,
                    )
                ]
            )
        ],
        status=fake.random_element(elements=STATUS),
        statusReason=[
            CodeableConcept.construct(
                coding=[
                    generate_coding(
                        "status-reason",
                        STATUS_REASON,
                    )
                ]
            )
        ],
        subject=generate_reference(subject, displayname(subject.name[0])),
    )


def mock_medication_statement(pseudonym: Pseudonym, patient: Patient, medications: Sequence[Medication]) -> None:
    # Generate medication statements in the past
    for medication in random.sample(medications, min(len(medications), 3)):
        write_and_store(
            generate_medication_statement(
                medication,
                patient,
                end_date=fake.date_this_year(before_today=True, after_today=False),
            ),
            pseudonym,
        )
    # Generate medication statements in the future
    for medication in random.sample(medications, min(len(medications), 3)):
        write_and_store(
            generate_medication_statement(
                medication,
                patient,
                start_date=fake.date_this_year(after_today=True, before_today=False),
            ),
            pseudonym,
        )
    # Generate current medication statements
    for medication in random.sample(medications, min(len(medications), 3)):
        write_and_store(
            generate_medication_statement(
            medication,
            patient,
            start_date=fake.date_between(start_date="-2w", end_date="today"),
            end_date=fake.date_between(start_date="today", end_date="+2w"),
            ),
            pseudonym,
        )
