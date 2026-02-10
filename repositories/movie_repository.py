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

def get_movies(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None
) -> Tuple[int, List[Tuple[Movie, float, int]]]:
    avg_subq = select(
        MovieRating.movie_id,
        func.avg(MovieRating.score).label("average_rating"),
        func.count(MovieRating.id).label("ratings_count")
    ).group_by(MovieRating.movie_id).subquery()

    query = select(
        Movie,
        func.coalesce(avg_subq.c.average_rating, 0),
        func.coalesce(avg_subq.c.ratings_count, 0)
    ).outerjoin(
        avg_subq, Movie.id == avg_subq.c.movie_id
    ).options(
        joinedload(Movie.director), joinedload(Movie.genres)
    )

    count_query = select(func.count(Movie.id.distinct())).outerjoin(
        avg_subq, Movie.id == avg_subq.c.movie_id
    )

    if title:
        query = query.where(Movie.title.ilike(f"%{title}%"))
        count_query = count_query.where(Movie.title.ilike(f"%{title}%"))
    if release_year:
        query = query.where(Movie.release_year == release_year)
        count_query = count_query.where(Movie.release_year == release_year)
    if genre:
        query = query.join(Movie.genres).where(Genre.name == genre)
        count_query = count_query.join(Movie.genres).where(Genre.name == genre)

    total = db.scalar(count_query)

    results = db.execute(
        query.order_by(Movie.id).offset((page - 1) * page_size).limit(page_size)
    ).unique().all()

    return total, [(movie, avg, count) for movie, avg, count in results]

