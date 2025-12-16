from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()

@router.get("/alive")
def is_alive():
    return {"status": "alive"}

@router.get("/ready")
def is_ready():
    # TODO: requete sur la base
    return {"status": "ready"}
