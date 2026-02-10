from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.movie_service import get_all_movies, get_movie_detail, create_new_movie, update_existing_movie, delete_existing_movie
from app.services.rating_service import add_rating
from app.schemas.movie import MovieCreate, MovieUpdate, PaginatedResponse, MovieDetailOut
from app.schemas.rating import RatingCreate, RatingOut

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@router.post("/", response_model=dict, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    data = create_new_movie(db, movie)
    return {"status": "success", "data": data}

@router.put("/{movie_id}", response_model=dict)
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db)):
    data = update_existing_movie(db, movie_id, movie)
    return {"status": "success", "data": data}

