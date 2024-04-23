import uuid
from enum import Enum
from typing import Optional


# DataDomain definitions
class DataDomain(Enum):
    BeeldBank = 'beeldbank'
    Medicatie = 'medicatie'

    @classmethod
    def from_str(cls, label: str) -> Optional['DataDomain']:
        try:
            return cls(label.lower())
        except ValueError:
            return None


# Pseudonym for a hashed BSN
Pseudonym = uuid.UUID


def str_to_pseudonym(pseudonym: str) -> Pseudonym|None:
    """
    Convert a string to a UUID pseudonym
    """
    try:
        return Pseudonym(pseudonym)
    except ValueError:
        return None


# Healthcare Provider ID
ProviderID = str
