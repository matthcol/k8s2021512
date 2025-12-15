from fastapi import FastAPI
from .database import Base, engine
from .routers import movies

app = FastAPI()

# Créer les tables
Base.metadata.create_all(bind=engine)

app.include_router(movies.router)
