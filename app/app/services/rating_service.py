from sqlalchemy.orm import Session
from app.repositories.rating_repository import create_rating
from app.repositories.movie_repository import get_movie_by_id
from app.schemas.rating import RatingCreate, RatingOut
from app.exceptions.custom_exceptions import NotFoundException, ValidationException

def add_rating(db: Session, movie_id: int, rating: RatingCreate) -> RatingOut:
    if rating.score < 1 or rating.score > 10:
        raise ValidationException("Score must be between 1 and 10")
    if get_movie_by_id(db, movie_id) is None:
        raise NotFoundException("Movie not found")
    db_rating = create_rating(db, movie_id, rating.score)
    return RatingOut(id=db_rating.id, movie_id=db_rating.movie_id, score=db_rating.score)