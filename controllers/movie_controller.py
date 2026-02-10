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

@router.get("/", response_model=dict)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    title: Optional[str] = Query(None),
    release_year: Optional[int] = Query(None),
    genre: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    data = get_all_movies(db, page, page_size, title, release_year, genre)
    return {"status": "success", "data": data}
@router.get("/{movie_id}", response_model=dict)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    data = get_movie_detail(db, movie_id)
    return {"status": "success", "data": data}