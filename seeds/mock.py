from app.data import Pseudonym
from seeds.image_study import mock_image_study
from seeds.medication_statement import mock_medication_statemnt


if __name__ == "__main__":
    mock_image_study(Pseudonym("bbf54282-3d58-4bed-b27b-dd4e1b85ec08"))
    mock_medication_statemnt(Pseudonym("c67230ce-0a28-4e06-9fe9-6ca218f92923"))
