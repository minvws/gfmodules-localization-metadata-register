from uuid import UUID
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.dosage import Dosage
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.patient import Patient
from typing_extensions import Final
from seeds.utils import (
    fake,
    generate_coding,
    generate_identifier,
    generate_period,
    generate_reference,
)
from fhir.resources.R4B.medicationstatement import MedicationStatement

STATUS: Final[tuple[str, ...]] = ("active", "inactive", "entered-in-error")


def generate_dosage() -> Dosage:
    return Dosage.construct()


def generate_medication_statement(
    medication: Medication, subject: Patient
) -> MedicationStatement:
    id = fake.uuid4()
    return MedicationStatement.construct(
        id=id,
        identifier=[generate_identifier("MedicationStatement", id)],
        status=fake.random_element(elements=STATUS),
        medicationReference=generate_reference(
            medication.resource_type, UUID(medication.id), str(medication.text)
        ),
        subject=generate_reference(
            subject.resource_type, UUID(subject.id), " ".join(map(str, subject.name))
        ),
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
        dosage=generate_dosage(),
    )
