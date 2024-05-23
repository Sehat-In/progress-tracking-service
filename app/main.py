from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

router = APIRouter(
    prefix="/api/v1",
    tags=["progress-tracking"],
    responses={404: {"description": "Not found"}},
)

@router.post("/goals/new-goal/", response_model=schemas.Goal)
def add_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    new_goal = models.Goal(**goal.model_dump())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal

@router.put("/goals/{goal_id}/update-goal/", response_model=schemas.Goal)
def update_goal(goal_id: int, goal_update: schemas.GoalUpdate, db: Session = Depends(get_db)):
    updated_goal = db.query(models.Goal).get(models.Goal.id == goal_id)

    if updated_goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    updated_goal.update(goal_update.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()

    return updated_goal

@router.delete("/goals/{goal_id}/delete-goal/")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    deleted_goal = db.query(models.Goal).get(models.Goal.id == goal_id)

    if deleted_goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    deleted_goal.delete(synchronize_session=False)
    db.commit()

@router.get("/goals/{goal_id}/", response_model=schemas.Goal)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.Goal).get(models.Goal.id == goal_id)

    if goal is None:
        raise HTTPException(status_code=404, detail=f"Goal with id {goal_id} not found.")
    
    return goal

@router.get("/{user_id}/goals/", response_model=list[schemas.Goal])
def get_all_user_goal(user_id: int, db: Session = Depends(get_db)):
    user_goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()

    if not user_goals:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not set any goal.")
    
    return user_goals

@router.post("/create-progress/", response_model=schemas.UserProgress)
def create_user_progress(user_progress: schemas.UserProgressCreate, db: Session = Depends(get_db)):
    new_user_progress = models.UserProgress(**user_progress.model_dump())
    db.add(new_user_progress)
    db.commit()
    db.refresh(new_user_progress)

    return new_user_progress

@router.put("/{user_id}/update-progress/", response_model=schemas.UserProgress)
def update_user_progress(user_id: int, user_progress_update: schemas.UserProgressUpdate, db: Session = Depends(get_db)):
    updated_user_progress = db.query(models.UserProgress).get(models.UserProgress.user_id == user_id)

    if updated_user_progress is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not initialized personal progress.")
    
    updated_user_progress.update(user_progress_update.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()

    return updated_user_progress

@router.delete("/{user_id}/clear-progress/")
def clear_user_progress(user_id: int, db: Session = Depends(get_db)):
    user_goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()

    if user_goals:
        for goal in user_goals:
            goal.delete(synchronize_session=False)
            db.commit()

@router.get("/{user_id}/progress/", response_model=schemas.UserProgress)
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    user_progress = db.query(models.UserProgress).get(models.UserProgress.user_id == user_id)

    if user_progress is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} has not initialized personal progress.")
    
    return user_progress

app.include_router(router)