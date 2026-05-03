from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    interactions: List["Interaction"] = Relationship(back_populates="contact")


class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    type: Optional[str] = Field(default="note")
    channel: Optional[str] = None
    notes: Optional[str] = None
    follow_up: bool = Field(default=False)

    contact: Optional[Contact] = Relationship(back_populates="interactions")
