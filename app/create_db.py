from app import application
from app import container

if __name__ == "__main__":
    application.application_init()

    db = container.get_database()
    db.generate_tables()
