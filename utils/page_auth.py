from fastapi import Request
from utils.jwt import decode_access_token
from db.database import SessionLocal
from db.models import User

def get_user_from_request(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
        return user
    finally:
        db.close()