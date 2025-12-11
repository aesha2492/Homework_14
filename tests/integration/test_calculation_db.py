from sqlalchemy.orm import Session
from app.models import Calculation, User
from app.schemas import CalcType
from app.services.factory import CalculationFactory


class TestCalculationDatabase:
    """Integration tests for Calculation model with database"""

    def test_create_calculation_in_db(self, db_session: Session):
        """Test creating and storing a Calculation in the database"""
        # Create a calculation
        calc = Calculation(
            a=10.0,
            b=5.0,
            type=CalcType.Add.value
        )
        
        # Add to session and commit
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        # Assert values stored correctly
        assert calc.id is not None
        assert calc.a == 10.0
        assert calc.b == 5.0
        assert calc.type == CalcType.Add.value
        assert calc.user_id is None

    def test_calculation_with_user_relationship(self, db_session: Session):
        """Test creating a Calculation with a User relationship"""
        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create a calculation for the user
        calc = Calculation(
            a=15.0,
            b=3.0,
            type=CalcType.Multiply.value,
            user_id=user.id
        )
        
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        # Assert relationship
        assert calc.user_id == user.id
        assert calc.user.username == "testuser"
        assert calc in user.calculations

    def test_calculation_result_with_factory(self, db_session: Session):
        """Test that calculated result matches factory computation"""
        # Test Add
        calc = Calculation(a=5.0, b=3.0, type=CalcType.Add.value)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        expected_result = CalculationFactory.execute(CalcType.Add, calc.a, calc.b)
        assert expected_result == 8.0
        
        # Test Subtract
        calc2 = Calculation(a=10.0, b=4.0, type=CalcType.Sub.value)
        db_session.add(calc2)
        db_session.commit()
        db_session.refresh(calc2)
        
        expected_result2 = CalculationFactory.execute(CalcType.Sub, calc2.a, calc2.b)
        assert expected_result2 == 6.0

    def test_calculation_divide_in_db(self, db_session: Session):
        """Test division calculation in database"""
        calc = Calculation(a=20.0, b=4.0, type=CalcType.Divide.value)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        expected_result = CalculationFactory.execute(CalcType.Divide, calc.a, calc.b)
        assert expected_result == 5.0

    def test_retrieve_calculation_from_db(self, db_session: Session):
        """Test retrieving a calculation from the database"""
        # Create and store
        calc = Calculation(a=7.0, b=2.0, type=CalcType.Multiply.value)
        db_session.add(calc)
        db_session.commit()
        calc_id = calc.id
        
        # Clear session and retrieve
        db_session.expunge_all()
        retrieved_calc = db_session.query(Calculation).filter(Calculation.id == calc_id).first()
        
        assert retrieved_calc is not None
        assert retrieved_calc.a == 7.0
        assert retrieved_calc.b == 2.0
        assert retrieved_calc.type == CalcType.Multiply.value

    def test_multiple_calculations_for_user(self, db_session: Session):
        """Test user having multiple calculations"""
        user = User(
            username="calcuser",
            email="calc@example.com",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Add multiple calculations
        calculations = [
            Calculation(a=1.0, b=2.0, type=CalcType.Add.value, user_id=user.id),
            Calculation(a=10.0, b=5.0, type=CalcType.Sub.value, user_id=user.id),
            Calculation(a=3.0, b=4.0, type=CalcType.Multiply.value, user_id=user.id),
        ]
        
        for calc in calculations:
            db_session.add(calc)
        
        db_session.commit()
        db_session.refresh(user)
        
        # Assert all are associated with user
        assert len(user.calculations) == 3
        assert all(calc.user_id == user.id for calc in user.calculations)
