import logging
from abc import ABC, abstractmethod
from dataclasses import asdict

import requests

from app.config import ConfigNVIAPI
from app.data import DataDomain
from app.services.models.create_referral_request_body import CreateReferralRequestBody
from app.services.models.referral import ReferralEntry

logger = logging.getLogger(__name__)


class NVIAPIServiceInterface(ABC):
    @abstractmethod
    def create_referral(self, body: CreateReferralRequestBody) -> ReferralEntry:
        raise NotImplementedError


class NVIAPIService(NVIAPIServiceInterface):
    _config: ConfigNVIAPI

    def __init__(self, config: ConfigNVIAPI) -> None:
        self._config = config

    def create_referral(self, body: CreateReferralRequestBody) -> ReferralEntry:
        logger.info(f"Creating new referral based on pseudonym {body.pseudonym}")
        response = self._send_post_request(body)

        data = response.json()
        attrs = data | {
            "data_domain": DataDomain(data["data_domain"]),
        }
        return ReferralEntry(**attrs)

    def _send_post_request(self, body: CreateReferralRequestBody) -> requests.Response:
        cert = (
            (self._config.mtls_cert, self._config.mtls_key)
            if self._config.mtls_cert and self._config.mtls_key
            else None
        )

        request_json = asdict(body)
        response = requests.post(
            f"{self._config.endpoint}/registrations/",
            json=request_json,
            cert=cert,
            verify=self._config.mtls_ca if self._config.mtls_ca else True,
        )
        if response.status_code != 200:
            raise ValueError(f"Failed to create referral: {response.status_code}")

        return response
