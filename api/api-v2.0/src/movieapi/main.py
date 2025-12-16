from fastapi import FastAPI
from .database import Base, engine
from .routers import movies, persons

app = FastAPI()


app.include_router(movies.router)
app.include_router(persons.router)
