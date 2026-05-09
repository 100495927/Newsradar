from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class InformationSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    url: HttpUrl

    @field_validator("name", mode="before")
    @classmethod
    def name_not_blank(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            raise ValueError("name no puede estar vacío o solo contener espacios")
        return v.strip() if isinstance(v, str) else v

    @field_validator("url", mode="before")
    @classmethod
    def url_not_blank(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            raise ValueError("url no puede estar vacía")
        return v


class InformationSourceCreate(InformationSourceBase):
    pass


class InformationSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    url: Optional[HttpUrl] = None


class InformationSource(InformationSourceBase):
    id: int


class RSSChannelBase(BaseModel):
    url: HttpUrl
    category_id: int

    @field_validator("url", mode="before")
    @classmethod
    def url_not_blank(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            raise ValueError("url no puede estar vacía")
        return v


class RSSChannelCreate(RSSChannelBase):
    pass


class RSSChannelUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    category_id: Optional[int] = None


class RSSChannel(RSSChannelBase):
    id: int
    information_source_id: int


