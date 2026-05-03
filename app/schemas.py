from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel


class InteractionCreate(SQLModel):
    date: Optional[datetime] = None
    type: Optional[str] = "note"
    channel: Optional[str] = None
    notes: Optional[str] = None
    follow_up: bool = False


class InteractionRead(SQLModel):
    id: int
    contact_id: int
    date: datetime
    type: Optional[str]
    channel: Optional[str]
    notes: Optional[str]
    follow_up: bool

    class Config:
        orm_mode = True


class ContactCreate(SQLModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class ContactRead(SQLModel):
    id: int
    name: str
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    tags: Optional[str]
    notes: Optional[str]
    created_at: datetime
    interactions: List[InteractionRead] = []

    class Config:
        orm_mode = True
