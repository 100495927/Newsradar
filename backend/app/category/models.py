from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, computed_field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    source: str = Field(..., pattern="^IPTC$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    source: Optional[str] = Field(None, pattern="^IPTC$")


class Category(CategoryBase):
    id: int

    @computed_field
    @property
    def code(self) -> str:
        return str(self.id).zfill(8)
