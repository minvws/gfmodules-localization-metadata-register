import uuid
from unittest.mock import MagicMock, patch

from app.config import ConfigNVIAPI
from app.data import DataDomain, Pseudonym, UraNumber
from app.services.models.create_referral_request_body import CreateReferralRequestBody
from app.services.nvi_api_service import NVIAPIService


@patch("app.services.nvi_api_service.requests.post")
def test_update_nvi_success(post_mock: MagicMock) -> None:
    post_mock.return_value.status_code = 200
    post_mock.return_value.json.return_value = {
        "pseudonym": "80b14956-f80a-4cd0-8bba-8678186f6a92",
        "data_domain": "beeldbank",
        "ura_number": "00000123",
    }

    config = ConfigNVIAPI(endpoint="http://localhost:8501")
    service = NVIAPIService(config)

    random_pseudonym = uuid.uuid4()

    data = CreateReferralRequestBody(
        pseudonym=Pseudonym(random_pseudonym),
        data_domain=DataDomain.BeeldBank,
        ura_number=UraNumber("123"),
        requesting_uzi_number="123",
    )
    result = service.create_referral(data)

    assert result is not None
