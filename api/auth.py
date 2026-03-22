from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas.auth import RegisterRequest, LoginRequest, UserResponse
from utils.hashing import hash_password, verify_password
from utils.jwt import create_access_token, get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if (
        existing_user := db.query(User)
        .filter(User.email == request.email)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post('/login')
def login(request:LoginRequest, response:Response, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token({'sub': str(user.id)})
    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        max_age=3600
    )
    return {'message': "Login Successful"}

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user