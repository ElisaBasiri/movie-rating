from sqlalchemy.orm import Session
from app.models.rating import MovieRating

def create_rating(db: Session, movie_id: int, score: int) -> MovieRating:
    db_rating = MovieRating(movie_id=movie_id, score=score)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating