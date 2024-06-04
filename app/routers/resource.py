import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, Body, HTTPException
from fhir.resources.bundle import Bundle

from app import container
from app.data import Pseudonym
from app.db.db import Database
from app.db.models import FhirResource

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resource/{pseudonym}",
            summary="Upload a resource to the metadata service",
            tags=["resources"]
            )
def post_resource(
    pseudonym: Pseudonym,
    resource: Dict[str, Any] = Body(...),
    db: Database = Depends(container.get_database)
) -> Any:

    if 'resourceType' not in resource:
        raise HTTPException(status_code=400, detail="Invalid or empty resourceType")
    if resource['resourceType'].lower() != "bundle":
        raise HTTPException(status_code=400, detail="Only bundle resources are supported")
    if 'type' not in resource:
        raise HTTPException(status_code=400, detail="Invalid or empty type")
    if resource['type'].lower() != "transaction":
        raise HTTPException(status_code=400, detail="Only transaction type is supported")

    bundle = Bundle.parse_obj(resource)
    if not bundle:
        raise HTTPException(status_code=400, detail="Invalid or empty bundle")

    session = db.get_db_session()

    # Iterate all resources and add them to the DB
    for entry in bundle.entry:
        resource = entry.resource.dict() # type: ignore
        if not resource:
            raise HTTPException(status_code=400, detail="Invalid or empty resource")
        if 'id' not in resource:
            raise HTTPException(status_code=400, detail="Invalid or empty resource id")
        if 'resourceType' not in resource:
            raise HTTPException(status_code=400, detail="Invalid or empty resourceType")

        res = FhirResource(
            id=uuid.uuid4(),
            pseudonym=pseudonym,
            resource_type=resource['resourceType'].lower(),
            resource_id=resource['id'].lower(),
            resource=resource,
        )
        session.add_resource(res)

    session.commit()

    return {
        "status": "ok",
        "message": "Resource uploaded successfully"
    }