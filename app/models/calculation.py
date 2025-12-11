from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # "Add", "Sub", "Multiply", "Divide"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship back to User
    user = relationship("User", back_populates="calculations")
