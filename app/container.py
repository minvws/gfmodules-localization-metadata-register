import inject

from app.config import Config, get_config
from app.db.db import Database
from app.metadata.db.db_adapter import DbMetadataAdapter
from app.metadata.metadata_service import MetadataService
from app.services.mock_nvi_api_service import MockNVIAPIService
from app.services.nvi_api_service import NVIAPIService, NVIAPIServiceInterface
from app.services.pseudonym_service import (
    MockPseudonymService,
    PseudonymService,
    PseudonymServiceInterface,
)


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn, create_tables=config.database.create_tables)
    binder.bind(Database, db)

    metadata_service = MetadataService(DbMetadataAdapter(db))
    binder.bind(MetadataService, metadata_service)

    _bind_pseudonym_service(config, binder)
    _bind_nvi_api_service(config, binder)


def get_nvi_service() -> NVIAPIServiceInterface:
    return inject.instance(NVIAPIServiceInterface)  # type: ignore[return-value]


def _bind_pseudonym_service(config: Config, binder: inject.Binder) -> None:
    if config.pseudonym_api.mock:
        binder.bind(PseudonymServiceInterface, MockPseudonymService())
        return

    pseudonym_service = PseudonymService(
        endpoint=config.pseudonym_api.endpoint,
        timeout=config.pseudonym_api.timeout,
        mtls_cert=config.pseudonym_api.mtls_cert,
        mtls_key=config.pseudonym_api.mtls_key,
        mtls_ca=config.pseudonym_api.mtls_ca,
    )
    binder.bind(PseudonymServiceInterface, pseudonym_service)


def _bind_nvi_api_service(config: Config, binder: inject.Binder) -> None:
    if config.nvi_api.mock:
        binder.bind(NVIAPIServiceInterface, MockNVIAPIService())
        return

    service = NVIAPIService(
        config=config.nvi_api,
    )
    binder.bind(NVIAPIServiceInterface, service)


def get_database() -> Database:
    return inject.instance(Database)


def get_metadata_service() -> MetadataService:
    return inject.instance(MetadataService)


def get_pseudonym_service() -> PseudonymServiceInterface:
    return inject.instance(PseudonymServiceInterface)  # type: ignore


def setup_container() -> None:
    inject.configure(container_config)
