from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.services.files import (
    delete_task_file,
    save_task_file,
)
from app.services.tasks import get_task


router = APIRouter(
    prefix="/tasks",
    tags=["Files"]
)


@router.post("/{task_id}/file")
def upload_file(
    task_id: int,
    file: UploadFile = File(...),
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

    try:
        task = save_task_file(
            db,
            task,
            file
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

    return {
        "message": "File uploaded successfully",
        "file_name": task.file_name
    }


@router.get("/{task_id}/file")
def download_file(
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

    if not task.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file attached to this task"
        )

    import os

    if not os.path.exists(task.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(
        path=task.file_path,
        filename=task.file_name
    )


@router.delete("/{task_id}/file")
def delete_file(
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

    if not task.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file attached to this task"
        )

    delete_task_file(
        db,
        task
    )

    return {
        "message": "File deleted successfully"
    }