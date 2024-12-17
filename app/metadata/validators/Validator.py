from typing import Protocol

from fhir.resources.R4B.resource import Resource


class InvalidResourceError(Exception):
    """
    Raised when the resource type is invalid
    """

    pass


class ValidationError(Exception):
    """
    Raised when the resource is not validated properly
    """

    pass


class Validator(Protocol):
    def validate(self, obj: Resource) -> None: ...
