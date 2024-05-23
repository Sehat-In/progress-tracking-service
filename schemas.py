from pydantic import BaseModel, validator
from typing import Optional
from models import GoalType, PeriodUnit

class GoalBase(BaseModel):
    user_id: int
    goal_type: GoalType
    value: float
    period: int
    period_unit: PeriodUnit
    progress: Optional[float] = 0.0
    progress_percentage: Optional[float] = 0.0
    is_completed: Optional[bool] = False

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    goal_type: Optional[GoalType]
    value: Optional[float]
    period: Optional[int]
    period_unit: Optional[PeriodUnit]
    progress: Optional[float]
    progress_percentage: Optional[float]
    is_completed: Optional[bool]

    @validator("goal_type", "value", "period", "period_unit", "progress", "progress_percentage", "is_completed", pre=True)
    def at_least_one_field_must_be_provided(cls, v, values):
        if all(v is None for v in values.values()):
            raise ValueError("At least one field must be provided for update")
        return v

class Goal(GoalBase):
    id: int

    class Config:
        from_attributes = True


class UserProgressBase(BaseModel):
    user_id: int
    overall_progress_percentage: Optional[float] = 0.0

class UserProgressCreate(UserProgressBase):
    pass

class UserProgressUpdate(BaseModel):
    overall_progress_percentage: float

class UserProgress(UserProgressBase):
    class Config:
        from_attributes = True
