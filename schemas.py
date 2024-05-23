from pydantic import BaseModel, root_validator
from typing import Optional
from models import GoalType, PeriodUnit
from fastapi import HTTPException

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
    goal_type: Optional[GoalType] = None
    value: Optional[float] = None
    period: Optional[int] = None
    period_unit: Optional[PeriodUnit] = None
    progress: Optional[float] = None
    progress_percentage: Optional[float] = None
    is_completed: Optional[bool] = None

    @root_validator(pre=True)
    def check_at_least_one_field(cls, values):
        if not any(value is not None for value in values.values()):
            raise HTTPException(
                status_code=400, 
                detail="At least one field must be provided for update"
            )
        return values

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
