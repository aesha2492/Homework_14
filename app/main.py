from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import schemas, crud
from .database import engine, Base, get_db
from app.routers import auth_router, calculations_router  # Include both routers
from fastapi.staticfiles import StaticFiles

# Create tables once at startup
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# Include routers
app.include_router(auth_router.router)
app.include_router(calculations_router.router)

# ---------- User Endpoints (backward compatible) ----------

@app.post("/users/", response_model=schemas.UserRead, status_code=201)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Old endpoint kept for backward compatibility with Module 11/12 tests"""
    user = crud.create_user(db, user_in)
    return user


@app.post("/users/register", response_model=schemas.UserRead, status_code=201)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Module 14 spec)"""
    user = crud.create_user(db, user_in)
    return user


@app.post("/users/login", response_model=schemas.UserRead)
def login_user(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return user info (still needed for existing tests)"""
    user = crud.authenticate_user(
        db, 
        email=user_in.email, 
        username=user_in.username,
        password=user_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return user


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------- Calculation BREAD Endpoints (Old, no auth for backward compatibility) ----------
# Note: For Module 14 authenticated endpoints, use /api/calculations/* instead

@app.post("/calculations/", response_model=schemas.CalculationRead, status_code=201)
def create_calculation(calc_in: schemas.CalculationCreate, db: Session = Depends(get_db)):
    """Create calculation (old endpoint without authentication)"""
    calculation = crud.create_calculation(db, calc_in)
    return calculation


@app.get("/calculations/", response_model=list[schemas.CalculationRead])
def read_all_calculations(db: Session = Depends(get_db)):
    """Get all calculations (old endpoint without authentication)"""
    calculations = crud.get_all_calculations(db)
    return calculations


@app.get("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    """Get specific calculation (old endpoint without authentication)"""
    calculation = crud.get_calculation_by_id(db, calc_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.put("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def update_calculation(
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    db: Session = Depends(get_db),
):
    """Update calculation (old endpoint without authentication)"""
    calculation = crud.update_calculation(db, calc_id, calc_in)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.delete("/calculations/{calc_id}", status_code=204)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    """Delete calculation (old endpoint without authentication)"""
    success = crud.delete_calculation(db, calc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return None
