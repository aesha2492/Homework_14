from abc import ABC, abstractmethod
from enum import Enum


class CalcType(str, Enum):
    """Enum for calculation types"""
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"


class Operation(ABC):
    """Abstract base class for operations"""

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Execute the operation and return the result"""
        pass


class Add(Operation):
    """Addition operation"""

    def execute(self, a: float, b: float) -> float:
        return a + b


class Sub(Operation):
    """Subtraction operation"""

    def execute(self, a: float, b: float) -> float:
        return a - b


class Multiply(Operation):
    """Multiplication operation"""

    def execute(self, a: float, b: float) -> float:
        return a * b


class Divide(Operation):
    """Division operation"""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


class CalculationFactory:
    """Factory to get the correct Operation instance"""

    _operations = {
        CalcType.Add: Add,
        CalcType.Sub: Sub,
        CalcType.Multiply: Multiply,
        CalcType.Divide: Divide,
    }

    @classmethod
    def get_operation(cls, operation_type: CalcType | str) -> Operation:
        """
        Get the correct operation instance based on type.
        
        Args:
            operation_type: CalcType enum or string representation
            
        Returns:
            Operation instance
            
        Raises:
            ValueError: If operation_type is not supported
        """
        # Convert string to CalcType if needed
        if isinstance(operation_type, str):
            try:
                operation_type = CalcType(operation_type)
            except ValueError:
                raise ValueError(f"Invalid operation type: {operation_type}. Must be one of {list(CalcType)}")

        if operation_type not in cls._operations:
            raise ValueError(f"Invalid operation type: {operation_type}")

        return cls._operations[operation_type]()

    @classmethod
    def execute(cls, operation_type: CalcType | str, a: float, b: float) -> float:
        """
        Execute an operation directly.
        
        Args:
            operation_type: CalcType enum or string representation
            a: First operand
            b: Second operand
            
        Returns:
            Result of the operation
        """
        operation = cls.get_operation(operation_type)
        return operation.execute(a, b)
