from fastapi import Depends, FastAPI, HTTPException
from app.services.tasks import get_tasks
from app.database import Base, engine
from app.models import User, Task
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.dependencies.auth import get_current_user
from app.middleware.middleware import log_requests
from fastapi.middleware.cors import CORSMiddleware
from app.routes.files import router as files_router
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from test_report import run_tests

Base.metadata.create_all(bind=engine)


app = FastAPI(title="TaskFlow API")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register middleware
app.middleware("http")(log_requests)


app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(files_router)


templates = Jinja2Templates(
    directory="templates"
)


@app.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = (
        db.query(User)
        .filter(User.id == current_user["user_id"])
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    tasks = get_tasks(
        db,
        current_user["user_id"]
    )

    total_tasks = len(tasks)

    # Count completed tasks
    completed_tasks = 0

    for task in tasks:
        if task.completed:
            completed_tasks += 1

    pending_tasks = total_tasks - completed_tasks

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "tasks": tasks,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks
        }
    )


@app.get("/")
def root():
    return {
        "message": "TaskFlow API is running"
    }

@app.get("/test-report")
def test_report(request: Request):

    report = run_tests()

    return templates.TemplateResponse(
        request=request,
        name="test_report.html",
        context={
            **report
        }
    )

