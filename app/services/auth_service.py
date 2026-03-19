from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.repositories.user_repo import get_user_by_email,get_user_by_username,create_user
from app.crypto import hash_password,verify_password,create_token_for_user
def register_user(db:Session,username:str,email:str,password:str):
    if get_user_by_username(db,username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
            )
    if get_user_by_email(db,email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
            )
    hashed_password = hash_password(password)
    return create_user(
        db,
        username=username,
        email=email,
        hashed_password=hashed_password
        )

def login_user(db:Session,username:str,password:str):
    user_indb = get_user_by_username(db,username)
    if not user_indb:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
            )
    if not verify_password(password,user_indb.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
            )
    token = create_access_token(user_indb.id,user.username)
    return token