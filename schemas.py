from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
from models import GoalType, PeriodUnit
from fastapi import HTTPException

class GoalBase(BaseModel):
    user_id: int
    goal_type: GoalType
    value: float = Field(..., gt=0, description="Goal value must be greater than 0")
    period: int = Field(..., gt=0, description="Goal period must be greater than 0")
    period_unit: PeriodUnit
    progress: Optional[float] = Field(0.0, ge=0, description="Progress must be non-negative")
    is_completed: Optional[bool] = False

    @validator('progress')
    def check_progress(cls, v, values):
        if 'value' in values and v > values['value']:
            raise ValueError('Progress must be between 0 and the goal value.')
        return v

    @property
    def progress_percentage(self):
        if self.value == 0:
            return 0.0
        return (self.progress / self.value) * 100

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    goal_type: Optional[GoalType] = None
    value: Optional[float] = None
    period: Optional[int] = None
    period_unit: Optional[PeriodUnit] = None
    progress: Optional[float] = None
    is_completed: Optional[bool] = None

    @root_validator(pre=True)
    def check_at_least_one_field(cls, values):
        if not any(value is not None for value in values.values()):
            raise HTTPException(
                status_code=400, 
                detail="At least one field must be provided for update"
            )
        return values
    
    @validator('value')
    def check_value(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Goal value must be greater than 0")
        return v

    @validator('period')
    def check_period(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Goal period must be greater than 0")
        return v

    @validator('progress')
    def check_progress(cls, v, values):
        if v is not None:
            if v < 0:
                raise ValueError("Progress must be non-negative")
            if 'value' in values and values['value'] is not None and v > values['value']:
                raise ValueError("Progress must be between 0 and the goal value")
        return v

class Goal(GoalBase):
    id: int
    progress_percentage: float

    class Config:
        from_attributes = True


class UserProgress(BaseModel):
    user_id: int
    overall_progress_percentage: float
    
    class Config:
        from_attributes = True
