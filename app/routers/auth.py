from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.services.auth_service import register_user,login_user
from app.schemas.user import UserCreate,UserLogin,UserResponse,TokenResponse
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = register_user(
        db,
        payload.username,
        payload.email,
        payload.password
    )
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = login_user(
        db,
        payload.username,
        payload.password
    )
    return {
        "accses_token":token,
        "token_type":"bearer"
    }