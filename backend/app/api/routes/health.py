from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.db.session import engine

router = APIRouter()


@router.get("/live", summary="Check whether the API process is running")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Check whether the database is reachable")
def readiness() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database is unavailable") from exc
    return {"status": "ok", "database": "connected"}
