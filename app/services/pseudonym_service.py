import logging
import uuid

import requests
from requests import HTTPError

from app.data import Pseudonym

logger = logging.getLogger(__name__)


class PseudonymError(Exception):
    pass


class PseudonymServiceInterface:
    def exchange(self, pseudonym: Pseudonym, provider_id: str) -> Pseudonym:
        raise NotImplementedError


class PseudonymService(PseudonymServiceInterface):
    def __init__(self, endpoint: str, timeout: int, mtls_cert: str, mtls_key: str, mtls_ca: str):
        self.endpoint = endpoint
        self.timeout = timeout
        self.mtls_cert = mtls_cert
        self.mtls_key = mtls_key
        self.mtls_ca = mtls_ca

    def exchange(self, pseudonym: Pseudonym, provider_id: str) -> Pseudonym:
        logger.info(f"Exchanging pseudonym {str(pseudonym)} for provider {provider_id}")

        try:
            req = requests.post(
                f"{self.endpoint}/exchange",
                json={
                    "source_pseudonym": str(pseudonym),
                    "target_provider_id": str(provider_id)
                },
                timeout=self.timeout,
                cert=(self.mtls_cert, self.mtls_key),
                verify=self.mtls_ca
            )
        except (Exception, HTTPError) as e:
            raise PseudonymError(f"Failed to exchange pseudonym: {e}")

        if req.status_code != 200:
            raise PseudonymError(f"Failed to exchange pseudonym: {req.status_code}")

        data = req.json()
        try:
            new_pseudonym = Pseudonym(data.get('pseudonym', ''))
        except ValueError:
            raise PseudonymError("Failed to exchange pseudonym: invalid pseudonym")

        return new_pseudonym


class MockPseudonymService(PseudonymServiceInterface):
    def __init__(self) -> None:
        pass

    def exchange(self, _pseudonym: Pseudonym, _provider_id: str) -> Pseudonym:
        return Pseudonym(str(uuid.uuid4()))
