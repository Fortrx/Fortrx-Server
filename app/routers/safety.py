from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.dependencies import get_active_user
from app.database import get_db
from app.services import fingerprint_service

router = APIRouter(
    prefix="/safety",
    tags=['safety']
)

@router.get("/numbers/{other_user_id}")
def get_numbers(
    other_user_id: int,
    current_user=Depends(get_active_user),
    db:Session=Depends(get_db)
):
    return fingerprint_service.get_safety_number(
        db,current_user.id,other_user_id
    )