import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, Body, HTTPException
from fhir.resources.bundle import Bundle

from app import container
from app.data import Pseudonym
from app.db.db import Database
from app.db.models import FhirResource, FhirReference

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resource/{pseudonym}",
            summary="Upload a resource to the metadata service",
            tags=["resources"]
            )
def post_resource(
    pseudonym: Pseudonym,
    data: Dict[str, Any] = Body(...),
    db: Database = Depends(container.get_database)
) -> Any:

    if 'resourceType' not in data:
        raise HTTPException(status_code=400, detail="Invalid or empty resourceType")
    if data['resourceType'].lower() != "bundle":
        raise HTTPException(status_code=400, detail="Only bundle resources are supported")
    if 'type' not in data:
        raise HTTPException(status_code=400, detail="Invalid or empty type")
    if data['type'].lower() != "transaction":
        raise HTTPException(status_code=400, detail="Only transaction type is supported")

    bundle = Bundle.parse_obj(data)
    if not bundle:
        raise HTTPException(status_code=400, detail="Invalid or empty bundle")

    session = db.get_db_session()

    # Iterate all resources and add them to the DB
    references = []
    for entry in bundle.entry:
        if not entry.resource:
            raise HTTPException(status_code=400, detail="Invalid or empty resource")
        if not entry.resource.id:
            raise HTTPException(status_code=400, detail="Invalid or empty resource id")
        if not entry.resource.resource_type:
            raise HTTPException(status_code=400, detail="Invalid or empty resourceType")

        res = FhirResource(
            id=uuid.uuid4(),
            resource_type=entry.resource.resource_type,
            resource_id=entry.resource.id,
            data=entry.resource.dict()
        )
        session.add_resource(res)

        references.append({
            "resource_type": entry.resource.resource_type,
            "resource_id": entry.resource.id
        })

    # Add reference entry for this pseudonym
    ref = FhirReference(
        id=uuid.uuid4(),
        pseudonym=pseudonym,
        references=references
    )
    session.add_resource(ref)

    session.commit()

    return {
        "status": "ok",
        "message": "Resource uploaded successfully"
    }