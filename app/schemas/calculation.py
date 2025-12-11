from pydantic import BaseModel, model_validator, computed_field, ConfigDict
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class CalcType(str, Enum):
    """Enum for calculation types"""
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"


class CalculationCreate(BaseModel):
    """Schema for creating a calculation"""
    a: float
    b: float
    type: CalcType

    @model_validator(mode='after')
    def check_divide_by_zero(self):
        """Validate that divisor is not zero when type is Divide"""
        if self.type == CalcType.Divide and self.b == 0:
            raise ValueError("Divisor (b) cannot be zero for Divide operation")
        return self


class CalculationRead(BaseModel):
    """Schema for reading a calculation with computed result"""
    id: int
    a: float
    b: float
    type: CalcType
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def result(self) -> float:
        """Compute result on-demand based on operation type"""
        if self.type == CalcType.Add:
            return self.a + self.b
        elif self.type == CalcType.Sub:
            return self.a - self.b
        elif self.type == CalcType.Multiply:
            return self.a * self.b
        elif self.type == CalcType.Divide:
            if self.b == 0:
                raise ValueError("Cannot divide by zero")
            return self.a / self.b
        else:
            raise ValueError(f"Unknown operation type: {self.type}")



class CalculationUpdate(BaseModel):
    """
    Schema for updating a calculation.
    All fields are optional to allow partial updates.
    """
    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[CalcType] = None

