from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm.exc import DetachedInstanceError
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    contacts: List["Contact"] = Relationship(back_populates="user")


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="contacts")
    interactions: List["Interaction"] = Relationship(back_populates="contact")

    @property
    def follow_up_needed(self) -> bool:
        try:
            return any(interaction.follow_up for interaction in self.interactions)
        except DetachedInstanceError:
            return False


class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: Optional[str] = Field(default="note")
    channel: Optional[str] = None
    notes: Optional[str] = None
    follow_up: bool = Field(default=False)
    follow_up_notes: Optional[str] = None

    contact: Optional[Contact] = Relationship(back_populates="interactions")
