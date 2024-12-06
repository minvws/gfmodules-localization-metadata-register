from dataclasses import dataclass

from app.data import DataDomain, Pseudonym, UraNumber


@dataclass
class CreateReferralRequestBody:
    pseudonym: Pseudonym

    data_domain: DataDomain
    ura_number: UraNumber
    requesting_uzi_number: str
