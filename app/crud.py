from sqlalchemy.orm import Session
from . import models, schemas, security
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def _to_dict(pydantic_obj, **kwargs) -> dict:
    """
    Support both Pydantic v1 (.dict) and v2 (.model_dump).
    """
    if hasattr(pydantic_obj, "model_dump"):
        return pydantic_obj.model_dump(**kwargs)
    return pydantic_obj.dict(**kwargs)


# ---------- USER CRUD ----------

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_pw = security.hash_password(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        # Unique constraint failed (username or email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )
    return db_user


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get user by email address"""
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str | None = None, username: str | None = None, password: str = None) -> models.User | None:
    """Authenticate user by email or username. Returns user if valid, None otherwise."""
    user = None
    if email:
        user = get_user_by_email(db, email)
    elif username:
        user = get_user_by_username(db, username)
    
    if not user or not security.verify_password(password, user.password_hash):
        return None
    return user


# ---------- CALCULATION CRUD ----------

def create_calculation(db: Session, calc_in: schemas.CalculationCreate, user_id: int | None = None) -> models.Calculation:
    data = _to_dict(calc_in)
    db_calc = models.Calculation(**data, user_id=user_id)
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


def get_user_calculations(db: Session, user_id: int) -> list[models.Calculation]:
    """Get all calculations for a specific user"""
    return db.query(models.Calculation).filter(models.Calculation.user_id == user_id).all()


def get_all_calculations(db: Session) -> list[models.Calculation]:
    return db.query(models.Calculation).all()


def get_calculation_by_id(db: Session, calc_id: int) -> models.Calculation | None:
    return db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()


def get_calculation_by_id_and_user(db: Session, calc_id: int, user_id: int) -> models.Calculation | None:
    """Get a calculation by ID, ensuring it belongs to the user"""
    return db.query(models.Calculation).filter(
        models.Calculation.id == calc_id,
        models.Calculation.user_id == user_id
    ).first()


def update_calculation(
    db: Session,
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    user_id: int | None = None,
) -> models.Calculation | None:
    if user_id is not None:
        calc = get_calculation_by_id_and_user(db, calc_id, user_id)
    else:
        calc = get_calculation_by_id(db, calc_id)
    
    if not calc:
        return None

    # Only update provided fields (exclude_unset)
    update_data = _to_dict(calc_in, exclude_unset=True)
    for field, value in update_data.items():
        setattr(calc, field, value)

    db.commit()
    db.refresh(calc)
    return calc


def delete_calculation(db: Session, calc_id: int, user_id: int | None = None) -> bool:
    if user_id is not None:
        calc = get_calculation_by_id_and_user(db, calc_id, user_id)
    else:
        calc = get_calculation_by_id(db, calc_id)
    
    if not calc:
        return False

    db.delete(calc)
    db.commit()
    return True

