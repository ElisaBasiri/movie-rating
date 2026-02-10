from sqlalchemy.orm import Session
from app.models.director import Director
from typing import Optional

def get_director_by_id(db: Session, director_id: int) -> Optional[Director]:
    return db.query(Director).filter(Director.id == director_id).first()