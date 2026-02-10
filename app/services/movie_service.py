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
import logging

def get_all_movies(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None
) -> PaginatedResponse:
    logger = logging.getLogger("movie_rating")
    logger.info(f"Fetching movie list (route=/api/v1/movies, page={page}, page_size={page_size}, title={title}, release_year={release_year}, genre={genre})")
    logger.debug(f"Query parameters: page={page}, page_size={page_size}, filters=(title={title}, release_year={release_year}, genre={genre})")
    try:
        total, movie_data = get_movies(db, page, page_size, title, release_year, genre)
        logger.debug(f"Total movies: {total}, data length: {len(movie_data)}")
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
        logger.info("Movie list fetched successfully")
        return PaginatedResponse(page=page, page_size=page_size, total_items=total, items=items)
    except Exception as e:
        logger.error("Failed to fetch movie list", exc_info=True)
        raise

def get_movie_detail(db: Session, movie_id: int) -> MovieDetailOut:
    logger = logging.getLogger("movie_rating")
    logger.info(f"Fetching movie detail (movie_id={movie_id}, route=/api/v1/movies/{movie_id})")
    logger.debug(f"Querying movie by id: {movie_id}")
    try:
        result = get_movie_by_id(db, movie_id)
        if not result:
            logger.warning(f"Movie not found (movie_id={movie_id})")
            raise NotFoundException("Movie not found")
        movie, avg_rating, ratings_count = result
        logger.debug(f"Fetched movie: title={movie.title}, ratings_count={ratings_count}")
        logger.info("Movie detail fetched successfully")
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
    except Exception as e:
        logger.error(f"Failed to fetch movie detail (movie_id={movie_id})", exc_info=True)
        raise

def create_new_movie(db: Session, movie: MovieCreate) -> MovieDetailOut:
    if not get_director_by_id(db, movie.director_id):
        raise ValidationException("Invalid director_id")
    for gid in movie.genres:
        if not get_genre_by_id(db, gid):
            raise ValidationException(f"Invalid genre_id: {gid}")
    db_movie = create_movie(db, movie)  # Capture the returned Movie object
    return get_movie_detail(db, db_movie.id)  # Use the ID from db_movie

def update_existing_movie(db: Session, movie_id: int, movie_update: MovieUpdate) -> MovieDetailOut:
    if movie_update.director_id is not None:
        if not get_director_by_id(db, movie_update.director_id):
            raise ValidationException("Invalid director_id")
    if movie_update.genres is not None:
        for gid in movie_update.genres:
            if not get_genre_by_id(db, gid):
                raise ValidationException(f"Invalid genre_id: {gid}")
    updated = update_movie(db, movie_id, movie_update)
    if not updated:
        raise NotFoundException("Movie not found")
    return get_movie_detail(db, movie_id)

def delete_existing_movie(db: Session, movie_id: int):
    if not delete_movie(db, movie_id):
        raise NotFoundException("Movie not found")

