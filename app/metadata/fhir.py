import importlib
import logging
from typing import Any, Dict

from fhir.resources.R4B.resource import Resource
from pydantic import BaseModel

logger = logging.getLogger(__name__)


ALLOWED_RESOURCES = [
    "Patient",
    "ImagingStudy",
    "Observation",
    "Practitioner",
    "Organization",
]


class OperationOutcomeDetail(BaseModel):
    text: str


class OperationOutcomeIssue(BaseModel):
    severity: str
    code: str
    details: OperationOutcomeDetail


class OperationOutcome(BaseModel):
    resourceType: str = "OperationOutcome"
    issue: list[OperationOutcomeIssue]


def convert_resource_to_fhir(data: Dict[str, Any]) -> Resource | None:
    """
    Convert a resource entry (database entry) to a FHIR resource model
    """
    if data is None:
        return None

    if "resourceType" not in data:
        logger.error("Resource type not found in resource")
        return None

    resource_type = data["resourceType"]
    if resource_type not in ALLOWED_RESOURCES:
        logger.error(f"Resource type {resource_type} not allowed")
        return None

    try:
        module = importlib.import_module(f"fhir.resources.R4B.{resource_type.lower()}")
        resource_class = getattr(module, resource_type, None)
        if resource_class:
            try:
                resource = resource_class.parse_obj(data)
                if isinstance(resource, Resource):
                    return resource
            except Exception as e:
                logger.error(f"Could not parse resource {data}: {e}")
                return None
        else:
            logger.error(f"Resource type {resource_type} is not supported.")

    except Exception as e:
        logger.error(f"Could not parse resource type {resource_type}: {e}")

    return None
