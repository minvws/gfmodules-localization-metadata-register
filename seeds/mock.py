from functools import partial
from app.data import Pseudonym
from seeds.medication import generate_medication
from seeds.medication_statement import generate_medication_statement
from seeds.organization import generate_organization
from seeds.patient import generate_patient
from seeds.utils import mocks_path, write_and_store


def mock_medication_statemnt(pseudonym: Pseudonym) -> None:
    _write_and_store = partial(
        write_and_store, dir=mocks_path(pseudonym), pseudonym=pseudonym
    )
    organization = generate_organization("Ziekthuis")
    _write_and_store(resource=organization)
    medication = generate_medication(organization)
    _write_and_store(resource=medication)
    patient = generate_patient()
    print(patient)
    _write_and_store(resource=patient)
    _write_and_store(resource=generate_medication_statement(medication, patient))


def mock_imaging(pseudonym: Pseudonym) -> None:
    pass


if __name__ == "__main__":
    mock_medication_statemnt(Pseudonym("c67230ce-0a28-4e06-9fe9-6ca218f92923"))
