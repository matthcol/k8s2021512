from sqlalchemy.orm import Session
from . import models, schemas

def create_movie(db: Session, movie: schemas.MovieCreate):
    db_film = models.Movie(**movie.model_dump())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

def get_movies(db: Session):
    return db.query(models.Movie).all()

def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()
