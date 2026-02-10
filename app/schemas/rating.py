from pydantic import BaseModel


class RatingCreate(BaseModel):
    score: int


class RatingOut(RatingCreate):
    id: int
    movie_id: int
    