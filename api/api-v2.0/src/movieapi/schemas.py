from datetime import date
from pydantic import BaseModel

class MovieBase(BaseModel):
    title: str
    year: int
    duration: int | None

class MovieCreate(MovieBase):
    pass

class MovieResponse(MovieBase):
    id: int

    class Config:
        orm_mode = True


class PersonBase(BaseModel):
    name: str
    birthdate: date | None


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: int

    class Config:
        orm_mode = True
