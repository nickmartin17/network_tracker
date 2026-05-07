from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str


class InteractionCreate(SQLModel):
    date: Optional[datetime] = None
    type: Optional[str] = "note"
    channel: Optional[str] = None
    notes: Optional[str] = None
    follow_up: bool = False
    follow_up_notes: Optional[str] = None


class InteractionRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    date: datetime
    type: Optional[str]
    channel: Optional[str]
    notes: Optional[str]
    follow_up: bool
    follow_up_notes: Optional[str]


class ContactCreate(SQLModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class ContactRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    tags: Optional[str]
    priority: Optional[str]
    notes: Optional[str]
    created_at: datetime
    interactions: List[InteractionRead] = []


class ContactListRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    tags: Optional[str]
    priority: Optional[str]
    notes: Optional[str]
    created_at: datetime
    follow_up_needed: bool = False
