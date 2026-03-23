import base64
from fastapi import HTTPException
from app.repositories import key_repo

def get_safety_number(db,local_user_id:int,remote_user_id:int):
    local_bundle = key_repo.get_bundle_by_user_id(db,local_user_id)
    remote_bundle = key_repo.get_bundle_by_user_id(db,remote_user_id)
    
    if not local_bundle or not remote_bundle:
        raise HTTPException(status_code=500,detail="Invalid Key Encoding")
    try:
        local_ik = base64.b64decode(local_bundle.identity_key)
        remote_ik = base64.b64decode(remote_bundle.identity_key)
    except Exception:
        raise HTTPException(status_code=500,detail="Invalid key encoding")
    
    from app.crypto.fingerprint import generate_safety_number
    
    result = generate_safety_number(
        local_user_id,
        local_ik,
        remote_user_id,
        remote_ik
    )
    return {
        "safety_number": result["safety_number"],
        "your_fingerprint": result["your_fingerprint"],
        "their_fingerprint": result["their_fingerprint"],
        "local_user_id":local_user_id,
        "remote_user_id":remote_user_id
    }