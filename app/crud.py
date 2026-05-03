from typing import List, Optional

from sqlmodel import Session, select

from .database import get_session
from .models import Contact, Interaction


def create_contact(contact: Contact) -> Contact:
    with get_session() as session:
        session.add(contact)
        session.commit()
        session.refresh(contact)
        return contact


def get_contacts(tag: Optional[str] = None) -> List[Contact]:
    with get_session() as session:
        statement = select(Contact).order_by(Contact.created_at.desc())
        if tag:
            statement = statement.where(Contact.tags.contains(tag))
        results = session.exec(statement).all()
        return results


def get_contact(contact_id: int) -> Optional[Contact]:
    with get_session() as session:
        return session.get(Contact, contact_id)


def create_interaction(contact_id: int, interaction: Interaction) -> Interaction:
    with get_session() as session:
        contact = session.get(Contact, contact_id)
        if not contact:
            raise ValueError("Contact not found")
        interaction.contact_id = contact_id
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return interaction


def get_interactions(contact_id: int) -> List[Interaction]:
    with get_session() as session:
        statement = select(Interaction).where(Interaction.contact_id == contact_id).order_by(Interaction.date.desc())
        return session.exec(statement).all()
