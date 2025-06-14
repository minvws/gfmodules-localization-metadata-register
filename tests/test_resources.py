import unittest
import uuid
from datetime import date
from typing import Any

from fastapi.testclient import TestClient
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.patient import Patient

from app.application import create_fastapi_app
from app.config import set_config
from tests.test_config import get_test_config

set_config(get_test_config())
app = create_fastapi_app()
client = TestClient(app)


class TestApi(unittest.TestCase):
    PATIENT_ID_1 = "123"
    PATIENT_ID_2 = "126"
    PSEUDONYM_1 = str(uuid.uuid4())
    PSEUDONYM_2 = str(uuid.uuid4())

    def test_main(self) -> None:
        # Main page retrieval
        response = client.get("/")
        assert response.status_code == 200

    def test_health(self) -> None:
        # Health page retrieval
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_not_existing(self) -> None:
        # Unknown page retrieval
        response = client.get("/this-page-does-not-exist")
        assert response.status_code == 404

    def test_resources(self) -> None:
        self.put_resource_fail1()
        self.put_resource_fail2()
        self.put_resource_fail3()
        self.put_resource_fail4()
        self.put_resource_fail6()
        self.put_resource_fail7()
        self.put_resource_fail8()
        self.get_resource1()
        # @TODO: We can find all resources for all pseudonyms
        # self.get_resource2()
        self.get_resource3()
        self.history1()
        self.delete1()
        self.delete2()

    def put_resource_fail1(self) -> None:
        # Put resource without resourceType
        response = client.put(
            url="/resource/patient/123",
            json={"name": "test"},
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "resourceType is required in the resource data"

    def put_resource_fail2(self) -> None:
        # Put resource with incorrect resourceType
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "ImagingStudy"},
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "resource type does not match the resource type in the URL"

    def put_resource_fail3(self) -> None:
        # Put resource without id
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "Patient"},
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "id is required in the resource data"

    def put_resource_fail4(self) -> None:
        # Incorrect pseudonym in the params
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "Patient"},
            params={"pseudonym": "foo"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Badly formed pseudonym"

    def put_resource_fail6(self) -> None:
        # Put resource with incorrect id
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "Patient", "id": "xxxx"},
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "id in the resource data does not match the resource id in the URL"

    def put_resource_fail7(self) -> None:
        # Put resource with correct id
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            content=self.get_patient_resource_json(self.PATIENT_ID_1),
            params={"pseudonym": self.PSEUDONYM_1},
        )

        assert response.status_code == 201  # Resource created
        assert response.json()["resourceType"] == "Patient"
        assert response.json()["id"] == self.PATIENT_ID_1
        assert response.headers["ETag"] == "1"

        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            content=self.get_patient_resource_json(self.PATIENT_ID_1, "Jane"),
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 200  # Resource already exists
        assert response.json()["resourceType"] == "Patient"
        assert response.json()["id"] == self.PATIENT_ID_1
        assert response.headers["ETag"] == "2"

    def put_resource_fail8(self) -> None:
        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "Patient", "id": f"{self.PATIENT_ID_1}"},
            params={"pseudonym": self.PSEUDONYM_1},
            headers={"If-Match": "2"},
        )
        assert response.headers["ETag"] == "3"
        assert response.status_code == 200

        response = client.put(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            json={"resourceType": "Patient", "id": f"{self.PATIENT_ID_1}"},
            params={"pseudonym": self.PSEUDONYM_1},
            headers={"If-Match": "2"},  # Using same if match but ETag and version are both 3
        )
        assert response.status_code == 412

    def get_resource1(self) -> None:
        # Get resource with correct pseudonym
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 200
        assert response.json()["resourceType"] == "Patient"
        assert response.json()["id"] == self.PATIENT_ID_1
        assert response.headers["Content-Type"] == "application/fhir+json"
        assert response.headers["ETag"] == "3"

    def get_resource2(self) -> None:
        # Get resource with incorrect pseudonym
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            params={"pseudonym": self.PSEUDONYM_2},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Metadata not found"

    def get_resource3(self) -> None:
        # Get unknown resource
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_2}",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Metadata not found"

    def history1(self) -> None:
        # Get history of resource
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}/_history/1",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 200
        assert response.json()["resourceType"] == "Patient"
        assert response.json()["id"] == self.PATIENT_ID_1
        assert response.json()["name"][0]["given"][0] == "John"
        assert response.headers["Content-Type"] == "application/fhir+json"
        assert response.headers["ETag"] == "1"

        # Get history of resource v2
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}/_history/2",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 200
        assert response.json()["resourceType"] == "Patient"
        assert response.json()["id"] == self.PATIENT_ID_1
        assert response.json()["name"][0]["given"][0] == "Jane"
        assert response.headers["Content-Type"] == "application/fhir+json"
        assert response.headers["ETag"] == "2"

        # Get history of resource v4 (not found)
        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}/_history/4",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Metadata not found"

    def delete1(self) -> None:
        # Delete unknown resource
        response = client.delete(
            url=f"/resource/patient/{self.PATIENT_ID_2}",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Metadata not found"

    def delete2(self) -> None:
        # Delete known resource
        response = client.delete(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 204

        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 410
        assert response.json()["detail"] == "Resource deleted"

        response = client.get(
            url=f"/resource/patient/{self.PATIENT_ID_1}/history/1",
            params={"pseudonym": self.PSEUDONYM_1},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"

    def get_patient_resource_json(self, id: str, given_name: str = "John") -> Any:
        patient = self.get_patient_resource(id, given_name)
        return patient.model_dump_json()

    @staticmethod
    def get_patient_resource(id: str, given_name: str = "John") -> Patient:
        return Patient(
            id=str(id),
            identifier=[
                Identifier(system="http://hospital.org/patients", value="12345"),
            ],
            name=[
                HumanName(
                    use="official",
                    family="Doe",
                    given=[given_name],
                )
            ],
            gender="male",
            birthDate=date(1980, 1, 1),
        )
