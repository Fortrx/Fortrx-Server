from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import message_repo,user_repo
from app.schemas import MessageSend

def send_message(db:Session,sender_id:int,payload:MessageSend):
    