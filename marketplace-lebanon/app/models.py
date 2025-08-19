from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class Currency(str, Enum):
    LBP = "LBP"
    USD = "USD"


class Category(str, Enum):
    TEXTBOOKS = "Textbooks"
    ELECTRONICS = "Electronics"
    FURNITURE = "Furniture"
    TRANSPORT = "Transport"
    CLOTHING = "Clothing"
    TUTORING = "Tutoring"
    OTHER = "Other"


class Condition(str, Enum):
    NEW = "New"
    LIKE_NEW = "Like New"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: EmailStr = Field(index=True, unique=True)
    password_hash: str
    university: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    listings: list["Listing"] = Relationship(back_populates="seller")
    received_messages: list["Message"] = Relationship(back_populates="recipient")
    sent_messages: list["Message"] = Relationship(back_populates="sender")

    UNIVERSITIES = [
        "AUB - American University of Beirut",
        "LAU - Lebanese American University",
        "LU - Lebanese University",
        "USJ - Université Saint-Joseph",
        "NDU - Notre Dame University-Louaize",
        "BAU - Beirut Arab University",
        "AUST - American University of Science and Technology",
        "UOB - University of Balamand",
        "Phoenicia University",
        "RHU - Rafik Hariri University",
    ]


class Listing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    price: float = Field(index=True, ge=0)
    currency: Currency = Field(index=True)
    category: Category = Field(index=True)
    condition: Condition = Field(index=True)
    university: str = Field(index=True)
    image_path: Optional[str] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    seller_id: int = Field(foreign_key="user.id")
    seller: Optional[User] = Relationship(back_populates="listings")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listing.id")
    sender_id: int = Field(foreign_key="user.id")
    recipient_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    listing: Optional[Listing] = Relationship()
    recipient: Optional[User] = Relationship(
        back_populates="received_messages",
        sa_relationship_kwargs={"foreign_keys": "Message.recipient_id"},
    )
    sender: Optional[User] = Relationship(
        back_populates="sent_messages",
        sa_relationship_kwargs={"foreign_keys": "Message.sender_id"},
    )