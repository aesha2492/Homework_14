import pytest
from pydantic import ValidationError
from app.schemas import CalculationCreate, CalcType


class TestCalculationSchema:
    """Test suite for Calculation schemas"""

    def test_calculation_create_valid(self):
        """Test creating a valid CalculationCreate schema"""
        calc = CalculationCreate(
            a=5.0,
            b=3.0,
            type=CalcType.Add
        )
        assert calc.a == 5.0
        assert calc.b == 3.0
        assert calc.type == CalcType.Add

    def test_calculation_create_with_divide_valid(self):
        """Test creating a valid CalculationCreate with Divide and non-zero divisor"""
        calc = CalculationCreate(
            a=10.0,
            b=2.0,
            type=CalcType.Divide
        )
        assert calc.a == 10.0
        assert calc.b == 2.0
        assert calc.type == CalcType.Divide

    def test_calculation_create_divide_by_zero_raises_error(self):
        """Test that Divide with b=0 raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                a=5.0,
                b=0.0,
                type=CalcType.Divide
            )
        # Check that the error message contains our validation message
        errors = exc_info.value.errors()
        assert any("Divisor (b) cannot be zero" in error.get('msg', '') for error in errors)

    def test_calculation_create_invalid_type_raises_error(self):
        """Test that invalid type value raises ValidationError"""
        with pytest.raises(ValidationError):
            CalculationCreate(
                a=5.0,
                b=3.0,
                type="InvalidType"
            )

    def test_calculation_create_with_all_calc_types(self):
        """Test creating calculations with all valid CalcType values"""
        valid_types = [CalcType.Add, CalcType.Sub, CalcType.Multiply, CalcType.Divide]
        
        for calc_type in valid_types:
            # Use b=1 for Divide to avoid validation error
            b = 1.0 if calc_type == CalcType.Divide else 3.0
            calc = CalculationCreate(
                a=5.0,
                b=b,
                type=calc_type
            )
            assert calc.type == calc_type

    def test_calculation_create_string_type_conversion(self):
        """Test that string type values are properly converted to CalcType"""
        calc = CalculationCreate(
            a=5.0,
            b=3.0,
            type="Add"
        )
        assert calc.type == CalcType.Add
        assert isinstance(calc.type, CalcType)
