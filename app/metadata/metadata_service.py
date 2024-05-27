from typing import Protocol

from app.data import DataDomain, ProviderID, Pseudonym
from app.metadata.models import MetadataEntry


class MetadataAdapter(Protocol):
    def search(self, provider_id: ProviderID|None, data_domain: DataDomain, pseudonym: Pseudonym) -> MetadataEntry | None:
        ...


class MetadataService:
    def __init__(self, adapter: MetadataAdapter):
        self.adapter = adapter

    def search(self, provider_id: ProviderID|None, data_domain: DataDomain, pseudonym: Pseudonym) -> MetadataEntry | None:
        return self.adapter.search(provider_id, data_domain, pseudonym)
