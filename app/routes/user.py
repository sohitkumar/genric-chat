from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.models.schemas import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from app.services.password import hash_password, verify_password_hash

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)) -> SignupResponse:
    existing = db.scalar(select(User).where(User.email == request.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=request.email, password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return SignupResponse(message="User created successfully", user_id=user.id)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == request.email))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password_hash(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(message="Login successful", user_id=user.id)