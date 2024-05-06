import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from opentelemetry import trace

from app import container
from app.data import DataDomain, str_to_pseudonym
from app.metadata.metadata_service import MetadataService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/drs/{provider_id}/{service_name}",
            summary="Search for metadata for a specific id and service",
            tags=["metadata"]
            )
def get_metadata(
        provider_id: str,
        service_name: str,
        pseudonym: str,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.provider_id", provider_id)
    span.set_attribute("data.service_name", service_name)
    span.set_attribute("data.pseudonym", pseudonym)

    pseudo = str_to_pseudonym(pseudonym)
    if pseudo is None:
        raise HTTPException(status_code=400, detail="Invalid or empty pseudonym")

    data_service = DataDomain.from_str(service_name.lower())
    if data_service is None:
        raise HTTPException(status_code=400, detail="Invalid service name")

    entry = service.search(provider_id, data_service, pseudo)
    if entry is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    return entry