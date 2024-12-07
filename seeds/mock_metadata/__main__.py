from app.data import Pseudonym
from seeds.mock_metadata.image_study import mock_image_study
from seeds.mock_metadata.medication import mock_medication
from seeds.mock_metadata.medication_statement import mock_medication_statemnt
from seeds.mock_metadata.organization import mock_organization
from seeds.mock_metadata.person import mock_patients, mock_practitioners


if __name__ == "__main__":
    pseudonym = Pseudonym("bbf54282-3d58-4bed-b27b-dd4e1b85ec08")
    patient = mock_patients(pseudonym)
    organizations = mock_organization(pseudonym)
    medications = mock_medication(pseudonym, organizations)
    mock_image_study(pseudonym, organizations, mock_practitioners(pseudonym), patient)
    mock_medication_statemnt(pseudonym, patient, medications)
