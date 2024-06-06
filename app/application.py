import logging

from typing import Any

from fastapi import FastAPI
import uvicorn

from app.container import setup_container
from app.telemetry import setup_telemetry
from app.routers.default import router as default_router
from app.routers.health import router as health_router
from app.routers.resource import router as metadata_router
from app.routers.resource import router as resource_router
from app.config import get_config


def get_uvicorn_params() -> dict[str, Any]:
    config = get_config()

    kwargs = {
        "host": config.uvicorn.host,
        "port": config.uvicorn.port,
        "reload": config.uvicorn.reload,
    }
    if config.uvicorn.use_ssl:
        kwargs["ssl_keyfile"] = f"{config.uvicorn.ssl_base_dir}/{config.uvicorn.ssl_key_file}"
        kwargs["ssl_certfile"] = f"{config.uvicorn.ssl_base_dir}/{config.uvicorn.ssl_cert_file}"
    return kwargs


def run() -> None:
    uvicorn.run("application:create_fastapi_app", **get_uvicorn_params())


def create_fastapi_app() -> FastAPI:
    application_init()
    fastapi = setup_fastapi()

    if get_config().telemetry.enabled:
        setup_telemetry(fastapi)

    return fastapi


def application_init() -> None:
    setup_container()
    setup_logging()


def setup_logging() -> None:
    loglevel = logging.getLevelName(get_config().app.loglevel.upper())

    if isinstance(loglevel, str):
        raise ValueError(f"Invalid loglevel {loglevel.upper()}")
    logging.basicConfig(
        level=loglevel,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )


def setup_fastapi() -> FastAPI:
    config = get_config()

    tags_metadata = [
        {
            "name": "default",
            "description": "Global operations"
        },
        {
            "name": "metadata",
            "description": "Metadata operations"
        }
    ]

    fastapi = (
        FastAPI(
            title="Metadata register",
            description="This register keeps metadata from different resources",
            docs_url=config.uvicorn.docs_url,
            redoc_url=config.uvicorn.redoc_url,
            openapi_tags=tags_metadata,
        ) if config.uvicorn.swagger_enabled else FastAPI(
            docs_url=None,
            redoc_url=None
        )
    )

    routers = [default_router, health_router, metadata_router, resource_router]
    for router in routers:
        fastapi.include_router(router)

    return fastapi
