from database import Base
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, Boolean, Enum as EnumSQL, TIMESTAMP, text
from sqlalchemy.orm import relationship

class GoalType(Enum):
    WEIGHTLOSS = "lose_weight"
    WEIGHTGAIN = "gain_weight"
    CALORIEINTAKE = "calorie_intake"
    CALORIEBURNED = "calorie_burned"

class PeriodUnit(Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    goal_type = Column(EnumSQL(GoalType), nullable=False)
    value = Column(Float, nullable=False)
    period = Column(Integer, nullable=False)
    period_unit = Column(EnumSQL(PeriodUnit), nullable=False)
    
    progress = Column(Float, server_default=text('0.0'))
    progress_percentage = Column(Float, server_default=text('0.0'))
    is_completed = Column(Boolean, server_default='false')

    user_progress = relationship("UserProgress", back_populates="goals")

class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(Integer, primary_key=True, index=True)
    overall_progress_percentage = Column(Float, server_default=text('0.0'))

    goals = relationship("Goal", back_populates="user_progress")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    