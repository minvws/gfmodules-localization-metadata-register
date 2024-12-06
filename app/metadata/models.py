from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class Physician(BaseModel):
    name: str
    ura: int


class Evaluation(BaseModel):
    type: str
    title: str
    description: str
    state: str
    physician: Physician


class HealthcareProvider(BaseModel):
    name: str
    ura: int


class MetadataEntry(BaseModel):
    id: str
    creation_date: datetime
    mutation_date: Optional[datetime] = None
    pseudonym: str
    evaluation: Evaluation
    healthcare_provider: HealthcareProvider
    metadata: Optional[dict[str, Any]] = {}
