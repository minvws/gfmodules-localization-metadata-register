from binascii import crc32

from faker import Faker

from app.data import DataDomain, Pseudonym, ProviderID
from app.metadata.metadata_service import MetadataAdapter
from app.metadata.models import MetadataEntry, Evaluation, Physician, HealthcareProvider


class MockMetadataAdapter(MetadataAdapter):
    def search(self, provider_id: ProviderID, data_domain: DataDomain, pseudonym: Pseudonym) -> MetadataEntry | None:
        faker = Faker('nl_NL')

        # Each unique combination results in a deterministic set of metadata
        seed = str(provider_id) + str(data_domain) + str(pseudonym)
        Faker.seed(crc32(seed.encode()))

        entry = MetadataEntry(
            id=faker.uuid4(),
            creation_date=faker.date_time_this_decade(),
            pseudonym=str(pseudonym),
            evaluation=Evaluation(
                type=faker.word(),
                title=faker.sentence(),
                description=faker.text(),
                state=faker.word(),
                physician=Physician(
                    name=faker.name(),
                    ura=faker.random_number(digits=8, fix_len=True)
                )
            ),
            healthcare_provider=HealthcareProvider(
                name=faker.company(),
                ura=faker.random_number(digits=8, fix_len=True)
            )
        )

        # Custom metadata for different data domains
        if data_domain == DataDomain.BeeldBank:
            images = []
            for i in range(0, 3):
                images.append({
                    'id': faker.uuid4(),
                    'url': faker.image_url(),
                    'description': faker.text()
                })

            entry.metadata = {
                'images': images
            }

        # Optionally add mutation info
        if faker.boolean(chance_of_getting_true=50):
            entry.mutation_date = faker.date_time_this_decade()

        return entry
