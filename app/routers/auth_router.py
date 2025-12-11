# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud, security
from app.database import get_db

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = crud.get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate username from email (remove domain part and sanitize)
    base_username = user_in.email.split("@")[0].lower()
    username = base_username
    counter = 1
    
    # Ensure username is unique
    while crud.get_user_by_username(db, username):
        username = f"{base_username}{counter}"
        counter += 1

    # Create user with generated username
    user_create = schemas.UserCreate(
        username=username,
        email=user_in.email,
        password=user_in.password
    )
    user = crud.create_user(db, user_create)

    # Create JWT
    access_token = security.create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    # Use your existing authentication helper if you have one
    user = crud.authenticate_user(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = security.create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
