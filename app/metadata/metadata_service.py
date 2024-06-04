from typing import Protocol, Sequence

from fhir.resources.resource import Resource

from app.data import Pseudonym


class MetadataAdapter(Protocol):
    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[Resource]:
        ...

    def search(self, resource_type: str, resource_id: str) -> Resource | None:
        ...

    def delete(self, resource_type: str, resource_id: str) -> None:
        ...


class MetadataService:
    def __init__(self, adapter: MetadataAdapter):
        self.adapter = adapter

    def search_by_pseudonym(self, pseudonym: Pseudonym, resource_type: str) -> Sequence[Resource]:
        return self.adapter.search_by_pseudonym(pseudonym, resource_type)

    def search(self, resource_type: str, resource_id: str) -> Resource | None:
        return self.adapter.search(resource_type, resource_id)

    def delete(self, resource_type: str, resource_id: str) -> None:
        return self.adapter.delete(resource_type, resource_id)