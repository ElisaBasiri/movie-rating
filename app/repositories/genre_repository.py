from sqlalchemy.orm import Session
from app.models.genre import Genre
from typing import Optional

def get_genre_by_id(db: Session, genre_id: int) -> Optional[Genre]:
    return db.query(Genre).filter(Genre.id == genre_id).first()