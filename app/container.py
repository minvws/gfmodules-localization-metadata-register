
import inject

from app.metadata.metadata_service import MetadataService
from app.metadata.mock.mock_adapter import MockMetadataAdapter


def container_config(binder: inject.Binder) -> None:
    metadata_service = MetadataService(MockMetadataAdapter())
    binder.bind(MetadataService, metadata_service)


def get_metadata_service() -> MetadataService:
    return inject.instance(MetadataService)


inject.configure(container_config)
