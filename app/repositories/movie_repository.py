from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.rating import MovieRating
from app.models.movie_genre import MovieGenre
from app.schemas.movie import MovieCreate, MovieUpdate
from typing import List, Optional, Tuple, Union


def create_movie(db: Session, movie: MovieCreate) -> Movie:
    db_movie = Movie(
        title=movie.title,
        release_year=movie.release_year,
        cast=movie.cast,
        director_id=movie.director_id
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    for genre_id in movie.genres:
        db.add(MovieGenre(movie_id=db_movie.id, genre_id=genre_id))
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(db: Session, movie_id: int, movie_update: MovieUpdate) -> Optional[Movie]:
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not db_movie:
        return None

    update_data = movie_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key != "genres":
            setattr(db_movie, key, value)

    if "genres" in update_data:
        db.query(MovieGenre).filter(MovieGenre.movie_id == movie_id).delete()
        for genre_id in movie_update.genres:
            db.add(MovieGenre(movie_id=movie_id, genre_id=genre_id))

    db.commit()
    db.refresh(db_movie)
    return db_movie

def delete_movie(db: Session, movie_id: int) -> bool:
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not db_movie:
        return False
    db.delete(db_movie)
    db.commit()
    return True
