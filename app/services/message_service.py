from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repositories import message_repo,user_repo
from app.schemas import MessageSend
from app.services import generate_blob_key,upload_blob,download_blob,delete_blob
from app.services.connection_manager import manager
import asyncio,websockets,base64

async def send_message(db:Session,sender_id:int,payload:MessageSend):
    recipient = user_repo.get_user_by_id(db,payload.reciepient_id)
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Recipient not found")
    
    blob_key = generate_blob_key(payload.reciepient_id)
    raw = base64.b64decode(payload.sealed_blob)
    upload_blob(blob_key,raw)

    message = message_repo.save_message(
        db=db,
        recipient_id=payload.reciepient_id,
        sealed_blob_key=blob_key,
        message_number=payload.message_number
    )
    
    await manager.send_to_user(
            payload.reciepient_id,{
                "type":"new_message",
                "message_id":message.id,
                "blob_key":blob_key,
                "message_number":payload.message_number
            }
        )
    return message

def fetch_inbox(db:Session,user_id:int):
    messages = message_repo.get_message_for_user(db,user_id)
    for msg in messages:
        raw = download_blob(msg.sealed_blob_key)
        msg.sealed_blob = base64.b64encode(raw).decode()
    return messages
        

def confirm_delivery(db:Session,message_id:int,user_id:int):
    message = db.query(message_repo.Message).filter(message_repo.Message.id==message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Message not found")
    
    if message.recipient_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    
    delete_blob(message_repo.Message.sealed_blob_key)
    
    message_repo.delete_message(db,message_id)
    return {"message":"deleted"}