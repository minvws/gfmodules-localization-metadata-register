from collections.abc import Callable
import random
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.patient import Patient

from seeds.utils import fake, generate_identifier


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


def generate_address() -> Address:
    return Address.construct(
        use="home",
        line=[fake.street_address()],
        city=fake.city(),
        postalCode=fake.postcode(),
        country="Netherlands",
    )


def generate_patient():
    uuid = fake.uuid4()
    gender = fake.random_element(
        elements=(
            ("male", fake.first_name_male),
            ("female", fake.first_name_female),
            ("other", fake.first_name_nonbinary),
            ("unknown", fake.first_name_nonbinary),
        )
    )

    return Patient.construct(
        id=uuid,
        identifier=[generate_identifier("patient", uuid)],
        active=True,
        address=[generate_address()],
        birth_date=fake.date_of_birth(),
        gender=gender[0],
        name=[generate_human_name(gender[1])],
        deceased_date=fake.past_date() if fake.random_number(digits=1) <= 2 else None,
    )
