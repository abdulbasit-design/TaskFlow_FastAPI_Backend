from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate
)
from app.services.tasks import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    update_task
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_task(
        db,
        task_data,
        current_user["user_id"]
    )


@router.get(
    "",
    response_model=list[TaskResponse]
)
def get_all(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_tasks(
        db,
        current_user["user_id"]
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_one(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id,
        current_user["user_id"]
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id,
        current_user["user_id"]
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return update_task(
        db,
        task,
        task_data
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id,
        current_user["user_id"]
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    delete_task(
        db,
        task
    )