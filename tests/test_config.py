from app.config import Config, ConfigApp, ConfigNVIAPI, LogLevel, ConfigDatabase, ConfigUvicorn, ConfigTelemetry, ConfigStats, \
    ConfigPseudonymApi


def get_test_config() -> Config:
    return Config(
        app=ConfigApp(
            loglevel=LogLevel.error,
            provider_id="1234",
        ),
        database=ConfigDatabase(
            dsn="sqlite:///:memory:",
            create_tables=True,
        ),
        pseudonym_api=ConfigPseudonymApi(
            mock=True,
            endpoint="http://pseudonym-api",
            timeout=1,
            mtls_cert="cert.pem",
            mtls_key="key.pem",
            mtls_ca="ca.pem",
        ),
        nvi_api=ConfigNVIAPI(
            mock=True,
            endpoint="http://localhost:8501",
            mtls_cert=None,
            mtls_key=None,
            mtls_ca=None,
        ),
        uvicorn=ConfigUvicorn(
            swagger_enabled=False,
            docs_url="/docs",
            redoc_url="/redoc",
            host="0.0.0.0",
            port=8503,
            reload=True,
            use_ssl=False,
            ssl_base_dir=None,
            ssl_cert_file=None,
            ssl_key_file=None,
        ),
        telemetry=ConfigTelemetry(
            enabled=False,
            endpoint=None,
            service_name=None,
            tracer_name=None,
        ),
        stats=ConfigStats(
            enabled=False,
            host=None,
            port=None,
            module_name=None
        )
    )
