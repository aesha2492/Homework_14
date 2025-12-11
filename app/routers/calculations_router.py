# app/routers/calculations_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud, security
from app.database import get_db

router = APIRouter(prefix="/api/calculations", tags=["calculations-authenticated"])


@router.post("/", response_model=schemas.CalculationRead, status_code=201)
def create_calculation(
    calc_in: schemas.CalculationCreate,
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db),
):
    """Add (CREATE) a new calculation for the logged-in user"""
    # Get user by email
    user = crud.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    calculation = crud.create_calculation(db, calc_in, user_id=user.id)
    return calculation


@router.get("/", response_model=list[schemas.CalculationRead])
def read_calculations(
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db),
):
    """Browse (READ) all calculations for the logged-in user"""
    # Get user by email
    user = crud.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    calculations = crud.get_user_calculations(db, user.id)
    return calculations


@router.get("/{calc_id}", response_model=schemas.CalculationRead)
def read_calculation(
    calc_id: int,
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db),
):
    """Read a specific calculation by ID (must belong to logged-in user)"""
    # Get user by email
    user = crud.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    calculation = crud.get_calculation_by_id_and_user(db, calc_id, user.id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have permission to access it",
        )
    return calculation


@router.put("/{calc_id}", response_model=schemas.CalculationRead)
def update_calculation(
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db),
):
    """Edit (UPDATE) a calculation (must belong to logged-in user)"""
    # Get user by email
    user = crud.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    calculation = crud.update_calculation(db, calc_id, calc_in, user_id=user.id)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have permission to update it",
        )
    return calculation


@router.delete("/{calc_id}", status_code=204)
def delete_calculation(
    calc_id: int,
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db),
):
    """Delete a calculation (must belong to logged-in user)"""
    # Get user by email
    user = crud.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    success = crud.delete_calculation(db, calc_id, user_id=user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have permission to delete it",
        )
    return None
