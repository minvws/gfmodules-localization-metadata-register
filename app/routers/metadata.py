import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fhir.resources.bundle import BundleEntry, Bundle
from fhir.resources.fhirtypes import Code, UnsignedInt, Id
from opentelemetry import trace
from starlette.responses import Response

from app import container
from app.data import Pseudonym
from app.metadata.metadata_service import MetadataService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search/{resource_type}",
    summary="Find all resources for given type for the pseudonym",
    tags=["metadata"]
)
def get_metadata(
        pseudonym: Pseudonym,
        resource_type: str,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.pseudonym", str(pseudonym))
    span.set_attribute("data.resource_type", resource_type)

    entry = service.search_by_pseudonym(pseudonym, resource_type)

    bundle = Bundle(     # type: ignore
        resource_type="Bundle",
        id=Id(uuid.uuid4()),
        type=Code("searchset"),
        total=UnsignedInt(len(entry)),
        entry=[BundleEntry(resource=res.dict()) for res in entry]  # type: ignore
    )

    return bundle.dict()


@router.get("/resource/{resource_type}/{resource_id}",
    summary="Find a specific type/id combination in the metadata",
    tags=["metadata"]
)
def get_resource_metadata(
        resource_type: str,
        resource_id: str,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    entry = service.search(resource_type, resource_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    return entry.dict()


@router.delete("/resource/{resource_type}/{resource_id}",
    summary="Removes a given type/id combination from the metadata",
    tags=["metadata"]
)
def delete_resource_metadata(
        resource_type: str,
        resource_id: str,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    entry = service.search(resource_type, resource_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    service.delete(resource_type, resource_id)

    return Response(status_code=204)
