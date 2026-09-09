import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.task import Task


UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".txt",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


def save_task_file(
    db: Session,
    task: Task,
    file: UploadFile
):
    # Get the original filename
    original_filename = file.filename

    if not original_filename:
        raise ValueError("File name is missing")

    # Get file extension
    extension = os.path.splitext(
        original_filename
    )[1].lower()

    # Validate extension
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("File type is not allowed")

    # Read file
    file_data = file.file.read()

    # Validate file size
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File size must be 5 MB or less")

    # Create task-specific directory
    task_directory = os.path.join(
        UPLOAD_DIR,
        str(task.id)
    )

    os.makedirs(
        task_directory,
        exist_ok=True
    )

    # Generate safe unique filename
    stored_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        task_directory,
        stored_filename
    )

    # Delete old file if task already has one
    if task.file_path and os.path.exists(task.file_path):
        os.remove(task.file_path)

    # Save actual file
    with open(file_path, "wb") as output_file:
        output_file.write(file_data)

    # Save file metadata in database
    task.file_name = original_filename
    task.file_path = file_path

    db.commit()
    db.refresh(task)

    return task


def delete_task_file(
    db: Session,
    task: Task
):
    if not task.file_path:
        return False

    if os.path.exists(task.file_path):
        os.remove(task.file_path)

    task.file_name = None
    task.file_path = None

    db.commit()
    db.refresh(task)

    return True