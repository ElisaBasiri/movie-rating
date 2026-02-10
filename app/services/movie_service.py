from typing import Dict, Any
from sqlalchemy.orm import Session
from app.repositories.movie_repository import get_movies, get_movie_by_id, create_movie, update_movie, delete_movie
from app.repositories.director_repository import get_director_by_id
from app.repositories.genre_repository import get_genre_by_id
from app.schemas.movie import MovieCreate, MovieUpdate, MovieListOut, MovieDetailOut, PaginatedResponse
from app.schemas.director import DirectorOut
from app.exceptions.custom_exceptions import NotFoundException, ValidationException
from typing import Optional
from app.models.movie import Movie  # Added import

def get_all_movies(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None
) -> PaginatedResponse:
    total, movie_data = get_movies(db, page, page_size, title, release_year, genre)
    items = []
    for movie, avg_rating, _ in movie_data:  # Ignore count for list
        items.append(MovieListOut(
            id=movie.id,
            title=movie.title,
            release_year=movie.release_year,
            director=DirectorOut(id=movie.director.id, name=movie.director.name),
            genres=[g.name for g in movie.genres],
            average_rating=round(float(avg_rating), 1)
        ))
    return PaginatedResponse(page=page, page_size=page_size, total_items=total, items=items)

def get_movie_detail(db: Session, movie_id: int) -> MovieDetailOut:
    result = get_movie_by_id(db, movie_id)
    if not result:
        raise NotFoundException("Movie not found")
    movie, avg_rating, ratings_count = result
    return MovieDetailOut(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        director=DirectorOut(id=movie.director.id, name=movie.director.name),
        genres=[g.name for g in movie.genres],
        average_rating=round(float(avg_rating), 1),
        cast=movie.cast,
        ratings_count=int(ratings_count),
        updated_at=movie.updated_at
    )

