import pytest
from app.services.factory import CalculationFactory, CalcType


class TestCalculationFactory:
    """Test suite for CalculationFactory"""

    def test_add_operation(self):
        """Test add operation returns correct result"""
        result = CalculationFactory.execute(CalcType.Add, 5, 3)
        assert result == 8

    def test_subtract_operation(self):
        """Test subtract operation returns correct result"""
        result = CalculationFactory.execute(CalcType.Sub, 5, 3)
        assert result == 2

    def test_multiply_operation(self):
        """Test multiply operation returns correct result"""
        result = CalculationFactory.execute(CalcType.Multiply, 5, 3)
        assert result == 15

    def test_divide_operation(self):
        """Test divide operation returns correct result"""
        result = CalculationFactory.execute(CalcType.Divide, 10, 2)
        assert result == 5

    def test_divide_by_zero_raises_error(self):
        """Test that divide by zero raises ValueError"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            CalculationFactory.execute(CalcType.Divide, 5, 0)

    def test_invalid_operation_type_raises_error(self):
        """Test that invalid operation type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid operation type"):
            CalculationFactory.get_operation("Invalid")

    def test_get_operation_returns_correct_instance(self):
        """Test that get_operation returns correct operation instance"""
        operation = CalculationFactory.get_operation(CalcType.Add)
        result = operation.execute(2, 3)
        assert result == 5

    @pytest.mark.parametrize("op_type,a,b,expected", [
        (CalcType.Add, 10, 5, 15),
        (CalcType.Sub, 10, 5, 5),
        (CalcType.Multiply, 10, 5, 50),
        (CalcType.Divide, 10, 5, 2),
    ])
    def test_all_operations_parametrized(self, op_type, a, b, expected):
        """Parametrized test for all operation types"""
        result = CalculationFactory.execute(op_type, a, b)
        assert result == expected
