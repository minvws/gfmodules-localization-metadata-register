import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends, Body, Query
from fhir.resources.bundle import BundleEntry, Bundle
from fhir.resources.fhirtypes import Code, UnsignedInt, Id
from opentelemetry import trace
from starlette.responses import Response

from app import container
from app.config import get_config
from app.data import Pseudonym
from app.metadata.fhir import convert_resource_to_fhir
from app.metadata.metadata_service import MetadataService
from app.metadata.validators.Validator import InvalidResourceError, ValidationError
from app.services.pseudonym_service import PseudonymService
from app.stats import get_stats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/resource/{resource_type}/_search",
            summary="Find all resources for given type for the pseudonym",
            tags=["metadata"]
            )
def search_resource(
        pseudonym: str,
        resource_type: str,
        service: MetadataService = Depends(container.get_metadata_service),
        pseudonym_service: PseudonymService = Depends(container.get_pseudonym_service)
) -> Any:
    span = trace.get_current_span()
    span.update_name(f"GET /resource/{resource_type}/_search?pseudonym={pseudonym}")
    span.set_attribute("data.pseudonym", pseudonym)
    span.set_attribute("data.resource_type", resource_type)

    get_stats().inc("http.get.resource.search")

    p = pseudonym_service.exchange(Pseudonym(pseudonym), get_config().app.provider_id)
    entry = service.search_by_pseudonym(p, resource_type)

    bundle = Bundle(  # type: ignore
        resource_type="Bundle",
        id=Id(uuid.uuid4()),
        type=Code("searchset"),
        total=UnsignedInt(len(entry)),
        entry=[BundleEntry(resource=res.resource) for res in entry]  # type: ignore
    )

    return bundle.dict()


@router.get("/resource/{resource_type}/{resource_id}/_history/{vid}",
            summary="Find a specific version of the resource in the metadata",
            tags=["metadata"]
            )
def get_resource_history(
        resource_type: str,
        resource_id: str,
        vid: int,
        _pretty: bool = False,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    return get_resource_by_version(resource_type, resource_id, vid, service, _pretty)


@router.get("/resource/{resource_type}/{resource_id}",
            summary="Find a specific type/id combination in the metadata",
            tags=["metadata"]
            )
def get_resource(
        resource_type: str,
        resource_id: str,
        _pretty: bool = False,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.update_name(f"GET /resource/{resource_type}/{resource_id}")
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    return get_resource_by_version(resource_type, resource_id, 0, service, _pretty)


@router.put("/resource/{resource_type}/{resource_id}",
            summary="Creates or updates a specific type/id combination in the metadata",
            tags=["metadata"]
            )
def put_resource(
        resource_type: str,
        resource_id: str,
        pseudonym: str = Query(required=False, default=None, description="Pseudonym to use for the resource"),
        data: Dict[str, Any] = Body(...),
        service: MetadataService = Depends(container.get_metadata_service),
        pseudonym_service: PseudonymService = Depends(container.get_pseudonym_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)
    span.set_attribute("data.pseudonym", pseudonym)

    p = None
    if pseudonym is not None:
        try:
            p = pseudonym_service.exchange(Pseudonym(pseudonym), get_config().app.provider_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Badly formed pseudonym")

    try:
        entry = service.update(resource_type, resource_id, data, p)
    except InvalidResourceError as e:
        logger.error(f"Invalid resource: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if entry is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    fhir_resource = convert_resource_to_fhir(entry.resource)
    if fhir_resource is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    return Response(
        content=fhir_resource.json(),
        media_type="application/fhir+json",
        status_code=201 if entry.version == 1 else 200,
        headers={
            "ETag": str(entry.version),
            "Last-Modified": entry.created_dt.isoformat(),
            "Location": f"/resource/{resource_type}/{resource_id}/_history/{entry.version}",
        }
    )


@router.delete("/resource/{resource_type}/{resource_id}",
               summary="Removes a given type/id combination from the metadata",
               tags=["metadata"]
               )
def delete_resource(
        resource_type: str,
        resource_id: str,
        service: MetadataService = Depends(container.get_metadata_service)
) -> Any:
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    entry = service.search(resource_type, resource_id, 0)
    if entry is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    service.delete(resource_type, resource_id)

    return Response(status_code=204)


@router.patch("/resource/{resource_type}/{resource_id}",
              summary="Patches a specific type/id combination in the metadata",
              tags=["metadata"]
              )
def patch_resource(
        resource_type: str,
        resource_id: str,
) -> Response:
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    # We do not support PATCH
    return Response(status_code=405)


def get_resource_by_version(resource_type: str, resource_id: str, vid: int, service: MetadataService,
                            pretty: bool = False) -> Response:
    """
    Get a resource from the metadata service based on the id and version. If vid == 0, it will fetch the
    latest version
    """
    span = trace.get_current_span()
    span.set_attribute("data.resource_type", resource_type)
    span.set_attribute("data.resource_id", resource_id)

    resource = service.search(resource_type, resource_id, vid)
    if resource is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    if resource.deleted:
        raise HTTPException(status_code=410, detail="Resource deleted")

    fhir_resource = convert_resource_to_fhir(resource.resource)
    if fhir_resource is None:
        raise HTTPException(status_code=404, detail="Metadata not found")

    return Response(
        content=fhir_resource.json(indent=2) if pretty else fhir_resource.json(),
        media_type="application/fhir+json",
        status_code=200,
        headers={
            "ETag": str(resource.version),
            "Last-Modified": resource.created_dt.isoformat(),
        }
    )
