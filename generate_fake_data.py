from faker import Faker
from models import Contact, User
from db import init_db, get_db
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./my_contacts_for_users_db.sqlite"


def generate_fake_data():

    fake = Faker()

    init_db()

    db: Session = next(get_db())

    try:
        for _ in range(10):
            contact = Contact(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone_number=fake.phone_number(),
                birth_date=fake.date_of_birth(),
                additional_data=fake.text()
            )
            db.add(contact)

        for _ in range(10):
            user = User(
                email=fake.email(),
                password=fake.password(),
                refresh_token=fake.uuid4()
            )
            db.add(user)

        db.commit()
        print("Fake data generated.")
    except Exception as e:
        db.rollback()
        print(f"Error!: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    generate_fake_data()
