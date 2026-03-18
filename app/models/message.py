from sqlalchemy import Integer,String,Column,Text,DateTime,Boolean,ForeignKey
from datetime import datetime
from app.database import Base

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer,primary_key=True,index=True)
    sender_id = Column(Integer,nullable=False)
    recipient_id = Column(Integer,nullable=False)
    ciphertext = Column(Text,nullable=False)
    header = Column(Text)
    message_number = Column(Integer)
    created_at = Column(DateTime,default=datetime.utcnow)
    expires_at = Column(DateTime,nullable=True)