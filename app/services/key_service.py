from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models import User
from app.repositories import get_bundle_by_user_id,create_bundle,update_bundle,pop_one_time_prekey
from app.schemas import KeyBundleUpload,KeyBundleResponse

def upload_key_bundle(db:Session,user_id:int,payload:KeyBundleUpload):
    bundle = get_bundle_by_user_id(db,user_id)
    if bundle:
        bundle= update_bundle(db,bundle,identity_key=payload.identity_key,signed_prekey=payload.signed_prekey,signed_prekey_signature=payload.signed_prekey_signature,prekey_id=payload.prekey_id,one_time_prekeys=payload.one_time_prekeys)
    else:
        bundle= update_bundle(db,user_id=user_id,identity_key=payload.identity_key,signed_prekey=payload.signed_prekey,signed_prekey_signature=payload.signed_prekey_signature,prekey_id=payload.prekey_id,one_time_prekeys=payload.one_time_prekeys)
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.identity_public_key = payload.identity_key
        db.commit()
    return bundle
    
def fetch_key_bundle(db:Session,user_id:int):
    bundle = get_bundle_by_user_id(db,user_id)
    if not bundle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Key Bundle not found")
    otp = pop_one_time_prekey(db,bundle)
    return KeyBundleResponse(
        user_id=bundle.user_id,
        identity_key=bundle.identity_key,
        signed_prekey=bundle.signed_prekey,
        signed_prekey_signature=bundle.signed_prekey_signature,
        prekey_id=bundle.prekey_id,
        one_time_prekkey=otp
        )