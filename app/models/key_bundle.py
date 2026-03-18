from sqlalchemy import Column,Integer,DateTime,Text
from datetime import datetime
from app.database import Base

class KeyBundle(Base):
    __tablename__ = "key_bundles"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,nullable=False,index=True)
    identity_key = Column(Text)
    signed_prekey = Column(Text)
    signed_prekey_signatue = Column(Text)
    prekey_id = Column(Integer)
    one_time_prekeys = Column(Text)
    updated_at = Column(DateTime,default=datetime.utcnow)