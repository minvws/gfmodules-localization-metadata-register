import inject

from app.config import get_config
from app.db.db import Database
from app.metadata.metadata_service import MetadataService
from app.metadata.db.db_adapter import DbMetadataAdapter


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn)
    binder.bind(Database, db)

    metadata_service = MetadataService(DbMetadataAdapter(db))
    binder.bind(MetadataService, metadata_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_metadata_service() -> MetadataService:
    return inject.instance(MetadataService)


inject.configure(container_config)
