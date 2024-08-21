import logging

from typing import Any

from fastapi import FastAPI
import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.container import setup_container
from app.metadata.fhir import OperationOutcome, OperationOutcomeIssue, OperationOutcomeDetail
from app.stats import setup_stats, StatsdMiddleware
from app.telemetry import setup_telemetry
from app.routers.default import router as default_router
from app.routers.health import router as health_router
from app.routers.resource import router as resource_router
from app.config import get_config


def get_uvicorn_params() -> dict[str, Any]:
    config = get_config()

    kwargs = {
        "host": config.uvicorn.host,
        "port": config.uvicorn.port,
        "reload": config.uvicorn.reload,
        "reload_delay": config.uvicorn.reload_delay,
        "reload_dirs": config.uvicorn.reload_dirs,
    }
    if (config.uvicorn.use_ssl and
            config.uvicorn.ssl_base_dir is not None and
            config.uvicorn.ssl_cert_file is not None and
            config.uvicorn.ssl_key_file is not None
    ):
        kwargs["ssl_keyfile"] = f"{config.uvicorn.ssl_base_dir}/{config.uvicorn.ssl_key_file}"
        kwargs["ssl_certfile"] = f"{config.uvicorn.ssl_base_dir}/{config.uvicorn.ssl_cert_file}"
    return kwargs


def run() -> None:
    uvicorn.run("app.application:create_fastapi_app", **get_uvicorn_params())


def create_fastapi_app() -> FastAPI:
    application_init()
    fastapi = setup_fastapi()

    if get_config().stats.enabled:
        setup_stats()

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

    routers = [default_router, health_router, resource_router]
    for router in routers:
        fastapi.include_router(router)

    if get_config().stats.enabled:
        fastapi.add_middleware(StatsdMiddleware, module_name=get_config().stats.module_name)

    fastapi.add_exception_handler(Exception, default_fhir_exception_handler)

    return fastapi


def default_fhir_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Default handler to convert generic exceptions to FHIR exceptions
    """
    outcome = OperationOutcome(issue=[
        OperationOutcomeIssue(
            severity="error",
            code="exception",
            details=OperationOutcomeDetail(text=f"{exc}")
        )
    ])

    return JSONResponse(
        status_code=500,
        content=outcome.model_dump()
    )
