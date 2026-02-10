from sqlalchemy.orm import Session
from app.repositories.rating_repository import create_rating
from app.repositories.movie_repository import get_movie_by_id
from app.schemas.rating import RatingCreate, RatingOut
from app.exceptions.custom_exceptions import NotFoundException, ValidationException
import logging

def add_rating(db: Session, movie_id: int, rating: RatingCreate) -> RatingOut:
    logger = logging.getLogger("movie_rating")
    logger.info(f"Rating movie (movie_id={movie_id}, rating={rating.score}, route=/api/v1/movies/{movie_id}/ratings)")
    logger.debug(f"Received rating request for movie_id={movie_id}, score={rating.score}")
    logger.debug(f"Checking score validity: {rating.score}")
    if rating.score < 1 or rating.score > 10:
        logger.warning(f"Invalid rating value (movie_id={movie_id}, rating={rating.score}, route=/api/v1/movies/{movie_id}/ratings)")
        raise ValidationException("Score must be between 1 and 10")
    logger.debug("Checking movie existence")
    if get_movie_by_id(db, movie_id) is None:
        logger.warning(f"Movie not found (movie_id={movie_id})")
        raise NotFoundException("Movie not found")
    try:
        logger.debug("Attempting to create rating")
        db_rating = create_rating(db, movie_id, rating.score)
        logger.debug(f"Created rating id={db_rating.id}")
        logger.info(f"Rating saved successfully (movie_id={movie_id}, rating={rating.score})")
        return RatingOut(id=db_rating.id, movie_id=db_rating.movie_id, score=db_rating.score)
    except Exception:
        logger.error(f"Failed to save rating (movie_id={movie_id}, rating={rating.score})", exc_info=True)
        raise