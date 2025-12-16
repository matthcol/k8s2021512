from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db

import movieapi.schemas as schemas
import movieapi.crud as crud

router = APIRouter()


@router.post("/persons/", response_model=schemas.PersonResponse)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db, person)

@router.get("/persons/", response_model=list[schemas.PersonResponse])
def list_persons(db: Session = Depends(get_db)):
    return crud.get_persons(db)

@router.get("/person/{person_id}", response_model=schemas.PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    movie = crud.get_person(db, person_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

