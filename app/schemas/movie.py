from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .director import DirectorOut


class MovieCreate(BaseModel):
    title: str
    director_id: int
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: List[int] = []


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    director_id: Optional[int] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: Optional[List[int]] = None


class MovieListOut(BaseModel):
    id: int
    title: str
    release_year: Optional[int]
    director: DirectorOut
    genres: List[str]
    average_rating: float


class MovieDetailOut(MovieListOut):
    cast: Optional[str]
    ratings_count: int
    updated_at: datetime


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total_items: int
    items: List[MovieListOut]
