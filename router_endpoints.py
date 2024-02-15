from fastapi import FastAPI, Depends, Query, HTTPException, APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta
from starlette import status
from db import get_db
from models import Contact, User
from auth_procedures import get_active_user
from typing import Optional
from sqlalchemy.orm import Session

app = FastAPI()

router = APIRouter(prefix='/contacts', tags=['contacts'])

app.include_router(router)


class UserContact(BaseModel):
    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: datetime
    additional_info: Optional[str] = None


@router.post("/contacts/")
def create_new_contact(contact: UserContact, session: Session = Depends(get_db),
                       current_user: User = Depends(get_active_user)):
    try:
        session.add(
            Contact(
                id=contact.contact_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                email=contact.email,
                phone_number=contact.phone_number,
                birth_date=contact.birth_date,
                additional_data=contact.additional_info
            )
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    return {"message": "Contact created successfully!", "status_code": status.HTTP_201_CREATED}


@router.get("/contacts/")
def get_all_contacts_list(session: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    contacts = session.query(Contact).all()
    return contacts


@router.get("/contacts/{contact_id}")
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/contacts/{contact_id}")
def update_contact(
    contact_id: int,
    updated_contact: UserContact,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    try:
        db_contact = session.query(Contact).get(contact_id)

        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        db_contact.first_name = updated_contact.first_name
        db_contact.last_name = updated_contact.last_name
        db_contact.email = updated_contact.email
        db_contact.phone_number = updated_contact.phone_number
        db_contact.birth_date = updated_contact.birth_date
        db_contact.additional_data = updated_contact.additional_info

        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    return {"message": "Success!"}


@router.delete("/contacts/{contact_id}")
def delete_contact(
        contact_id: int,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    db_contact = session.query(Contact).get(contact_id)

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    session.delete(db_contact)
    session.commit()

    return {"message": "Success!","status_code": status.HTTP_204_NO_CONTENT}


@router.get("/contacts/")
def get_specific_contacts_list(session: Session = Depends(get_db), search: str = Query(None),
                               current_user: User = Depends(get_active_user)):
    if search:
        contacts = session.query(Contact).filter(
            (Contact.first_name.ilike(f"%{search}%")) |
            (Contact.last_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        ).all()
    else:
        contacts = session.query(Contact).all()
    return contacts


@router.get("/contacts/birthdays/")
def get_upcoming_birthdays(session: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    today = datetime.today()
    end_date = today + timedelta(days=7)

    upcoming_birthdays = session.query(Contact).filter(
        (Contact.birth_date >= today) & (Contact.birth_date <= end_date)
    ).all()

    return upcoming_birthdays
