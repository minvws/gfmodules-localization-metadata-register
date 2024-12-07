from collections.abc import Callable
import random
from typing_extensions import Final
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.practitioner import Practitioner

from app.data import Pseudonym
from seeds.mock_metadata.utils import fake, generate_identification, write_and_store

PRACTICIONS: Final[tuple[tuple[str, str], ...]] = (
    ("Dokter", "Bibber"),
    ("Zuster", "Bloedwijn"),
    ("Oogarts", "Appel"),
    ("Radioloog", "Straal"),
)

N_PATIENTS = 2


def generate_first_names(gender_faker: Callable[[], str]) -> list[str]:
    return [
        gender_faker()
        for _ in range(
            random.choices(
                population=[1, 2, 3, 4],
                weights=[0.7, 0.2, 0.07, 0.03],
                k=1,
            )[0]
        )
    ]


def generate_human_name(gender: Callable[[], str]) -> HumanName:
    return HumanName.construct(
        family=fake.last_name(),
        given=generate_first_names(gender),
    )


def generate_address(use: str) -> Address:
    return Address.construct(
        use=use,
        line=[fake.street_address()],
        city=fake.city(),
        postalCode=fake.postcode(),
        country="Netherlands",
    )


def generate_patient():
    gender = fake.random_element(
        elements=(
            ("male", fake.first_name_male),
            ("female", fake.first_name_female),
            ("other", fake.first_name_nonbinary),
            ("unknown", fake.first_name_nonbinary),
        )
    )

    return Patient.construct(
        **generate_identification("patient"),
        active=True,
        address=[generate_address("home")],
        birth_date=fake.date_of_birth(),
        gender=gender[0],
        name=[generate_human_name(gender[1])],
        deceased_date=fake.past_date() if fake.random_number(digits=1) <= 2 else None,
    )


def generate_practitioner(family: str, given: str):
    return Practitioner.construct(
        **generate_identification("practitioner"),
        active=True,
        address=[generate_address("work")],
        birth_date=fake.date_of_birth(),
        name=[HumanName.construct(family=family, given=[given])],
    )


def mock_practitioners(pseudonym: Pseudonym):
    return [write_and_store(generate_practitioner(*name), pseudonym) for name in PRACTICIONS]


def mock_patients(pseudonym: Pseudonym):
    return write_and_store(generate_patient(), pseudonym)
