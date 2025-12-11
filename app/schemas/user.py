from pydantic import BaseModel, EmailStr, constr, ConfigDict, model_validator
from datetime import datetime

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)

class UserRegister(BaseModel):
    """Schema for JWT-based registration (email + password only)"""
    email: EmailStr
    password: constr(min_length=8)

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    """Login schema that accepts either username or email"""
    username: str | None = None
    email: str | None = None  # Allow any string format here, let API validate
    password: str
    
    @model_validator(mode='after')
    def at_least_one_provided(self):
        """Ensure at least one of username or email is provided"""
        if not self.username and not self.email:
            raise ValueError('Either username or email must be provided')
        return self
