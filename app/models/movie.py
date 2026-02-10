from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    release_year = Column(Integer)
    cast = Column(String)
    director_id = Column(Integer, ForeignKey("directors.id", ondelete="CASCADE"), nullable=False)
   

    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary="movie_genres", back_populates="movies")
    ratings = relationship("MovieRating", back_populates="movie", cascade="all, delete")
