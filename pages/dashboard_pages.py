from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.jwt import decode_access_token
from db.database import SessionLocal
from db.models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    user = get_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})