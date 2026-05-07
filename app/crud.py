from typing import List, Optional

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from .database import get_session
from .models import Contact, Interaction


def create_contact(contact: Contact) -> Contact:
    with get_session() as session:
        session.add(contact)
        session.commit()
        session.refresh(contact)
        return contact


def get_contacts(user_id: int, tag: Optional[str] = None) -> List[Contact]:
    with get_session() as session:
        statement = (
            select(Contact)
            .where(Contact.user_id == user_id)
            .options(selectinload(Contact.interactions))
            .order_by(Contact.created_at.desc())
        )
        if tag:
            statement = statement.where(Contact.tags.contains(tag))
        results = session.exec(statement).all()
        priority_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(
            key=lambda contact: (
                priority_order.get((contact.priority or "").lower(), 3),
                -contact.created_at.timestamp(),
            )
        )
        return results


def get_contact(user_id: int, contact_id: int) -> Optional[Contact]:
    with get_session() as session:
        statement = select(Contact).where(Contact.id == contact_id).options(selectinload(Contact.interactions))
        contact = session.exec(statement).first()
        if contact and contact.user_id == user_id:
            return contact
        return None


def update_contact(user_id: int, contact_id: int, **kwargs) -> Optional[Contact]:
    with get_session() as session:
        contact = session.get(Contact, contact_id)
        if not contact or contact.user_id != user_id:
            return None
        for key, value in kwargs.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        return contact


def delete_contact(user_id: int, contact_id: int) -> bool:
    with get_session() as session:
        contact = session.get(Contact, contact_id)
        if not contact or contact.user_id != user_id:
            return False
        session.delete(contact)
        session.commit()
        return True


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


def get_interactions(user_id: int, contact_id: int) -> List[Interaction]:
    with get_session() as session:
        # Verify the contact belongs to the user
        contact = session.get(Contact, contact_id)
        if not contact or contact.user_id != user_id:
            return []
        statement = select(Interaction).where(Interaction.contact_id == contact_id).order_by(Interaction.date.desc())
        return session.exec(statement).all()


def update_interaction(user_id: int, contact_id: int, interaction_id: int, **kwargs) -> Optional[Interaction]:
    with get_session() as session:
        # Verify contact belongs to user
        contact = session.get(Contact, contact_id)
        if not contact or contact.user_id != user_id:
            return None
        
        interaction = session.get(Interaction, interaction_id)
        if not interaction or interaction.contact_id != contact_id:
            return None
        
        for key, value in kwargs.items():
            if hasattr(interaction, key):
                setattr(interaction, key, value)
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return interaction


def delete_interaction(user_id: int, contact_id: int, interaction_id: int) -> bool:
    with get_session() as session:
        # Verify contact belongs to user
        contact = session.get(Contact, contact_id)
        if not contact or contact.user_id != user_id:
            return False
        
        interaction = session.get(Interaction, interaction_id)
        if not interaction or interaction.contact_id != contact_id:
            return False
        
        session.delete(interaction)
        session.commit()
        return True
