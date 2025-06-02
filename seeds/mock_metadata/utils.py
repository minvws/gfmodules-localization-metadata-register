import decimal
from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
import random
from typing import TypedDict
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.reference import Reference
from typing_extensions import Any, Final, TypeVar, override
from uuid import UUID
from faker import Faker
from pathlib import Path
import json
from fhir.resources.R4B.resource import Resource

from app.config import get_config
from app.data import Pseudonym
from app.db.db import Database
from app.metadata.db.db_adapter import DbMetadataAdapter
from app.metadata.metadata_service import MetadataService

fake = Faker("nl_NL")
config = get_config()


METADATA_SERVICE: Final[MetadataService] = MetadataService(
    DbMetadataAdapter(
        Database(dsn=config.database.dsn, create_tables=config.database.create_tables)
    )
)
URI_EXAMPLE: Final[str] = "https://example.org"
T = TypeVar("T", bound=Resource)


class CustomJSONEncoder(json.JSONEncoder):
    @override
    def default(self, o: Any) -> str:
        if type(o) in (datetime, date):
            return o.isoformat()
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)


def json_dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=4, cls=CustomJSONEncoder)


def store(resource: Resource, pseudonym: Pseudonym) -> None:
    if (
        METADATA_SERVICE.update(
            resource.get_resource_type(),
            resource.id,
            data=json.loads(json_dumps(resource.dict())),
            pseudonym=pseudonym,
        )
        is None
    ):
        raise Exception("Failed to store resource")


def mocks_path(pseudonym: Pseudonym) -> Path:
    path = Path(f"mocks/{pseudonym}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def component_filepath(path: Path, component: str, id: UUID) -> Path:
    return (path / f"{component}-{id}").with_suffix(".json")


def write_component(filepath: Path, data: dict[str, Any]) -> None:
    filepath.write_text(data=json_dumps(data), encoding="utf-8")


def write_and_store(resource: T, pseudonym: Pseudonym, dir: Path | None = None) -> T:
    if not dir:
        dir = mocks_path(pseudonym)
    write_component(
        component_filepath(dir, resource.get_resource_type().lower(), UUID(resource.id)),
        resource.dict(),
    )
    store(resource, pseudonym)
    return resource


def generate_reference(resource: T, name: str | None = None) -> Reference:
    return Reference.construct(
        reference=resource.relative_path(),
        display=name or fake.word(),
        type=resource.get_resource_type().capitalize(),
    )


def generate_identifier(component: str, value: str) -> Identifier:
    return Identifier.construct(system=f"{URI_EXAMPLE}/{component}", value=value)


def generate_coding(route: str, display_strings: Sequence[str] | None = None) -> Coding:
    return Coding.construct(
        system=f"{URI_EXAMPLE}/{route}",
        code=str(random.randint(100000, 999999)),
        display=(
            fake.random_element(elements=display_strings)
            if display_strings
            else fake.word().capitalize()
        ),
    )


def _generate_period(
    start: date | None = None, end: date | None = None
) -> dict[str, date]:
    time_range = timedelta(weeks=5)

    def generate(start: date|None=None, end: date|None=None) -> dict[str, date]:
        start = fake.date_between(start_date=start, end_date=end) if start is None else start
        end = fake.date_between(start_date=start, end_date=end) if end is None else end
        tz_start = datetime.combine(start, datetime.min.time()).replace(tzinfo=timezone.utc)
        tz_end = datetime.combine(end, datetime.min.time()).replace(tzinfo=timezone.utc)
        return {"start": tz_start, "end": tz_end}

    match start, end:
        case None, None:
            first = fake.date_time_this_year()
            return generate(first, first + time_range)
        case start, None:
            return generate(start, start + time_range)
        case None, end:
            return generate(end - time_range, end)
        case start, end:
            return generate(start, end)


def generate_period(start: date | None = None, end: date | None = None) -> Period:
    return Period(**_generate_period(start, end))


class Identification(TypedDict):
    id: UUID
    identifier: list[Identifier]


def generate_identification(component: str) -> Identification:
    return Identification(
        id=(id := fake.uuid4()), identifier=[generate_identifier(component, id)]
    )


def displayname(name: HumanName):
    return f"{name.given[0]} {name.family}"
