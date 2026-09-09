from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(
    db: Session,
    task_data: TaskCreate,
    user_id: int
):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=user_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks(
    db: Session,
    user_id: int
):
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .all()
    )


def get_task(
    db: Session,
    task_id: int,
    user_id: int
):
    return (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == user_id
        )
        .first()
    )


def update_task(
    db: Session,
    task: Task,
    task_data: TaskUpdate
):
    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    db: Session,
    task: Task
):
    db.delete(task)
    db.commit()