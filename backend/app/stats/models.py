from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Metric(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    value: float


class StatsBase(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)


class StatsCreate(StatsBase):
    pass


class StatsUpdate(BaseModel):
    metrics: Optional[List[Metric]] = None


class Stats(StatsBase):
    id: int


# Dashboard models

class CategoryCount(BaseModel):
    id: str
    total: int


class GlobalDashboard(BaseModel):
    n_fuentes: int
    n_canales_rss: int
    n_noticias: int
    n_alertas: int
    alertas_por_categoria: List[CategoryCount]
    noticias_por_categoria: List[CategoryCount]


class FeedStats(BaseModel):
    feed_id: int
    n_noticias: int
    n_alertas: int


class TimelineEntry(BaseModel):
    fecha: str
    total: int


class WordCloudItem(BaseModel):
    word: str
    value: int
