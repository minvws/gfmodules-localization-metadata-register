import inject

from app.config import get_config
from app.db.db import Database
from app.metadata.metadata_service import MetadataService
from app.metadata.db.db_adapter import DbMetadataAdapter
from app.services.pseudonym_service import PseudonymService, PseudonymServiceInterface, MockPseudonymService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn, create_tables=config.database.create_tables)
    binder.bind(Database, db)

    metadata_service = MetadataService(DbMetadataAdapter(db))
    binder.bind(MetadataService, metadata_service)

    if config.pseudonym_api.mock:
        binder.bind(PseudonymServiceInterface, MockPseudonymService())
    else:
        pseudonym_service = PseudonymService(
            endpoint=config.pseudonym_api.endpoint,
            timeout=config.pseudonym_api.timeout,
            mtls_cert=config.pseudonym_api.mtls_cert,
            mtls_key=config.pseudonym_api.mtls_key,
            mtls_ca=config.pseudonym_api.mtls_ca,
        )
        binder.bind(PseudonymServiceInterface, pseudonym_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_metadata_service() -> MetadataService:
    return inject.instance(MetadataService)


def get_pseudonym_service() -> PseudonymServiceInterface:
    return inject.instance(PseudonymServiceInterface)   # type: ignore


def setup_container() -> None:
    inject.configure(container_config)
