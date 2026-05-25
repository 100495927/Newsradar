from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AlertCategoryItem(BaseModel):
    code: str = Field(..., min_length=1, max_length=60)
    label: str = Field(..., min_length=1, max_length=120)


class AlertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    prioridad: int = Field(..., ge=1, le=3)
    descriptors: List[str] = Field(default_factory=list)
    categories: List[AlertCategoryItem] = Field(default_factory=list)
    rss_channels_ids: List[str] = Field(default_factory=list)
    information_sources_ids: List[str] = Field(default_factory=list)
    cron_expression: str = Field(..., min_length=1, max_length=120)


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    descriptors: Optional[List[str]] = None
    categories: Optional[List[AlertCategoryItem]] = None
    rss_channels_ids: Optional[List[str]] = None
    information_sources_ids: Optional[List[str]] = None
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=120)


class Alert(AlertBase):
    id: int
    user_id: int


NotificationChannel = Literal["app", "email"]


class AlertNotificationSettings(BaseModel):
    channels: List[NotificationChannel] = Field(default_factory=lambda: ["app", "email"])


class AlertNotificationSettingsUpdate(BaseModel):
    channels: List[NotificationChannel] = Field(..., min_length=1)
