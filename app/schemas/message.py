from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageSend(BaseModel):
    reciepient_id:int
    sealed_blob:str
    message_number:int
    
class MessageResponse(BaseModel):
    id:int
    recipient_id:int
    sealed_blob:str
    message_number:int
    created_at:datetime
    expires_at: Optional[datetime]
    
    class Config():
        from_attributes=True