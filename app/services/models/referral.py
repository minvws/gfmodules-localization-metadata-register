from dataclasses import dataclass

from app.data import DataDomain, UraNumber


@dataclass
class ReferralEntry:
    pseudonym: str
    data_domain: DataDomain
    ura_number: UraNumber
