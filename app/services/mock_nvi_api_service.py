from app.services.models.create_referral_request_body import CreateReferralRequestBody
from app.services.models.referral import ReferralEntry
from app.services.nvi_api_service import NVIAPIServiceInterface


class MockNVIAPIService(NVIAPIServiceInterface):
    def create_referral(self, body: CreateReferralRequestBody) -> ReferralEntry:
        return ReferralEntry(
            str(body.pseudonym),
            data_domain=body.data_domain,
            ura_number=body.ura_number,
        )
