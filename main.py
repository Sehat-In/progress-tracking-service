from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [os.getenv('CORS_ORIGIN')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api/v1",
    tags=["progress-tracking"],
    responses={404: {"description": "Not found"}},
)

def calculate_overall_progress(goals: list[schemas.Goal]):
    if not goals:
        return 0

    total_progress = sum(goal.progress_percentage for goal in goals)
    overall_progress = total_progress / len(goals)
    return overall_progress

def update_user_progress(user_id: int, db: Session = Depends(get_db)):
    updated_user_progress = db.query(models.UserProgress).filter(models.UserProgress.user_id == user_id).first()

    if updated_user_progress is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not initialized personal progress.")
    
    user_goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()
    updated_user_progress.overall_progress_percentage = calculate_overall_progress(user_goals)

    db.commit()
    db.refresh(updated_user_progress)

@router.post("/goals/new-goal/", response_model=schemas.Goal, status_code=status.HTTP_201_CREATED)
def add_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    new_goal_data = goal.model_dump()
    new_goal_data['progress_percentage'] = goal.progress_percentage
    new_goal = models.Goal(**new_goal_data)

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    update_user_progress(goal.user_id, db)

    return new_goal

@router.put("/goals/{goal_id}/update-goal/", response_model=schemas.Goal, status_code=status.HTTP_200_OK)
def update_goal(goal_id: int, goal_update: schemas.GoalUpdate, db: Session = Depends(get_db)):
    updated_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()

    if updated_goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    update_data = goal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(updated_goal, key, value)
        
        if key == 'progress':
            setattr(updated_goal, 'progress_percentage', (updated_goal.progress / updated_goal.value) * 100)

    db.commit()
    db.refresh(updated_goal)

    update_user_progress(updated_goal.user_id, db)

    return updated_goal

@router.delete("/goals/{goal_id}/delete-goal/", status_code=status.HTTP_200_OK)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    deleted_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()

    if deleted_goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    db.delete(deleted_goal)
    db.commit()

    update_user_progress(deleted_goal.user_id, db)

    return f"Goal with id {goal_id} has been deleted."

@router.get("/goals/{goal_id}/", response_model=schemas.Goal, status_code=status.HTTP_200_OK)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()

    if goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    return goal

@router.get("/{user_id}/goals/", response_model=list[schemas.Goal], status_code=status.HTTP_200_OK)
def get_all_user_goal(user_id: int, db: Session = Depends(get_db)):
    user_goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()

    if not user_goals:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not set any goal.")
    
    return user_goals

@router.post("/{user_id}/create-progress/", response_model=schemas.UserProgress, status_code=status.HTTP_201_CREATED)
def create_user_progress(user_id: int, db: Session = Depends(get_db)):
    existing_progress = db.query(models.UserProgress).filter(models.UserProgress.user_id == user_id).first()

    if existing_progress:
        return existing_progress
    
    new_user_progress = models.UserProgress(user_id=user_id)
    
    db.add(new_user_progress)
    db.commit()
    db.refresh(new_user_progress)

    return new_user_progress

@router.delete("/{user_id}/clear-progress/", status_code=status.HTTP_200_OK)
def clear_user_progress(user_id: int, db: Session = Depends(get_db)):
    user_progress = db.query(models.UserProgress).filter(models.UserProgress.user_id == user_id).first()

    if user_progress is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not initialized personal progress.")
    else:
        user_progress.overall_progress_percentage = 0
        db.commit()
        db.refresh(user_progress)
        
        user_goals = db.query(models.Goal).filter(models.Goal.user_id == user_id)

        if user_goals:
            for goal in user_goals:
                db.delete(goal)
                db.commit()
        
        return f"Progress of user with id {user_id} has been cleared."

@router.get("/{user_id}/progress/", response_model=schemas.UserProgress, status_code=status.HTTP_200_OK)
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    user_progress = db.query(models.UserProgress).filter(models.UserProgress.user_id == user_id).first()

    if user_progress is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not initialized personal progress.")
    
    return user_progress

app.include_router(router)