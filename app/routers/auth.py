from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import register_user,login_user
from app.schemas.user import UserCreate,UserLogin,UserResponse,TokenResponse
from app.database import get_db
from app.dependencies import get_active_user

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
def login(
    payload:OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    token = login_user(
        db,
        payload.username,
        payload.password
    )
    return {
        "access_token":token,
        "token_type":"bearer"
    }
    
@router.get("/me",response_model=UserResponse)
def get_me(current_user:User = Depends(get_active_user)):
    return current_user