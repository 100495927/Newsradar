from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Metric(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float


class StatsBase(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)


class StatsCreate(StatsBase):
    pass


class StatsUpdate(BaseModel):
    metrics: Optional[List[Metric]] = None


class Stats(StatsBase):
    id: int
