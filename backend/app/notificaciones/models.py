from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ..alertas.models import NotificationChannel
from ..stats.models import Metric


class NotificationBase(BaseModel):
    timestamp: datetime
    metrics: List[Metric] = Field(default_factory=list)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    metrics: Optional[List[Metric]] = None


class Notification(NotificationBase):
    id: int
    alert_id: int


class NotificationMatch(BaseModel):
    rss_entry_id: Optional[str] = None
    rss_entry_hash: Optional[str] = None
    title: str = ""
    link: str = ""
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    matched_descriptors: List[str] = Field(default_factory=list)
    category_id: Optional[int] = None


class NotificationMailboxItem(BaseModel):
    id: int
    alert_id: int
    user_id: int
    timestamp: datetime
    subject: str
    metrics: List[Metric] = Field(default_factory=list)
    matches: List[NotificationMatch] = Field(default_factory=list)
    delivery_channels: List[NotificationChannel] = Field(default_factory=list)
    email_status: str
    email_sent_at: Optional[datetime] = None
    email_error: Optional[str] = None
    read_at: Optional[datetime] = None


class NotificationReadState(BaseModel):
    id: int
    read_at: datetime
