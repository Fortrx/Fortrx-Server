from sqlalchemy.orm import Session
from app.models import Message
from datetime import datetime

def save_message(db:Session,sender_id,recipient_id,ciphertext,header,message_number):
    message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        ciphertext=ciphertext,
        header=header,
        message_number=message_number
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_message_for_user(db:Session,user_id:int):
    return (
        db.query(Message)
        .filter(Message.recipient_id==user_id)
        .order_by(Message.created_at.asc())
        .all()
    )

def get_conversation(db:Session,user_a: int,user_b:int):
    return (
        db.query(Message).filter(
            ((Message.sender_id==user_a)&(Message.recipient_id==user_b)) |
            ((Message.sender_id==user_b)&(Message.recipient_id==user_a))
        )
        .order_by(Message.message_number.asc())
        .all()
    )

def delete_message(db:Session,message_id:int):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
    return message

def get_expired_messages(db:Session):
    return (
        db.query(Message)
        .filter(
            Message.expires_at.isnot(None),
            Message.expires_at < datetime.utcnow()
        )
        .all()
    )