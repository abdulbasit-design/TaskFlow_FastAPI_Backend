import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ============================================================
# Helper Functions
# ============================================================

def create_test_user():
    email = f"pytest_{uuid.uuid4().hex}@example.com"
    password = "password123"

    response = client.post(
        "/auth/register",
        json={
            "name": "Pytest User",
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 201

    return email, password


def get_auth_token():
    email, password = create_test_user()

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_test_task():
    token = get_auth_token()

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Created by pytest"
        }
    )

    assert response.status_code == 201

    task = response.json()

    return token, task["id"]


# ============================================================
# NON-PROTECTED ROUTES
# ============================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "TaskFlow API is running"


def test_register_user():
    email = f"register_{uuid.uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Register User",
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Register User"
    assert data["email"] == email
    assert "password" not in data


def test_register_duplicate_email():
    email = f"duplicate_{uuid.uuid4().hex}@example.com"

    first_response = client.post(
        "/auth/register",
        json={
            "name": "First User",
            "email": email,
            "password": "password123"
        }
    )

    assert first_response.status_code == 201

    response = client.post(
        "/auth/register",
        json={
            "name": "Another User",
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Email already registered"


def test_register_short_password():
    email = f"short_{uuid.uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Short Password",
            "email": email,
            "password": "123"
        }
    )

    assert response.status_code == 422


def test_login_user():
    email = f"login_{uuid.uuid4().hex}@example.com"
    password = "password123"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    email = f"wrong_password_{uuid.uuid4().hex}@example.com"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Wrong Password User",
            "email": email,
            "password": "password123"
        }
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"


def test_login_nonexistent_email():
    response = client.post(
        "/auth/login",
        json={
            "email": f"does_not_exist_{uuid.uuid4().hex}@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"


# ============================================================
# JWT AUTHENTICATION
# ============================================================

def test_get_tasks_without_token():
    response = client.get("/tasks")

    assert response.status_code == 401


def test_get_tasks_with_invalid_token():
    response = client.get(
        "/tasks",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid or expired token"


def test_get_tasks_with_valid_token():
    token = get_auth_token()

    response = client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ============================================================
# TASK CRUD
# ============================================================

def test_create_task():
    token = get_auth_token()

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Created during pytest"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Created during pytest"
    assert data["completed"] is False
    assert "id" in data


def test_get_all_tasks():
    token = get_auth_token()

    create_response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Get All Task",
            "description": "Testing GET all"
        }
    )

    assert create_response.status_code == 201

    response = client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_single_task():
    token, task_id = create_test_task()

    response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Test Task"


def test_update_task():
    token, task_id = create_test_task()

    response = client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Updated Task",
            "description": "Updated by pytest",
            "completed": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated by pytest"
    assert data["completed"] is True


def test_delete_task():
    token, task_id = create_test_task()

    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code == 404


# ============================================================
# TASK OWNERSHIP
# ============================================================

def test_user_cannot_access_another_users_task():
    user1_token, task_id = create_test_task()

    user2_token = get_auth_token()

    response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {user2_token}"
        }
    )

    assert response.status_code == 404


# ============================================================
# FILE UPLOAD
# ============================================================

def test_upload_file():
    token, task_id = create_test_task()

    response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "test.txt",
                b"Hello from pytest",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "File uploaded successfully"
    assert data["file_name"] == "test.txt"


def test_download_file():
    token, task_id = create_test_task()

    upload_response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "download_test.txt",
                b"Download test content",
                "text/plain"
            )
        }
    )

    assert upload_response.status_code == 200

    response = client.get(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.content == b"Download test content"


def test_delete_file():
    token, task_id = create_test_task()

    upload_response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "delete_test.txt",
                b"Delete this file",
                "text/plain"
            )
        }
    )

    assert upload_response.status_code == 200

    response = client.delete(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "File deleted successfully"


def test_upload_file_without_token():
    _, task_id = create_test_task()

    response = client.post(
        f"/tasks/{task_id}/file",
        files={
            "file": (
                "no_auth.txt",
                b"No authentication",
                "text/plain"
            )
        }
    )

    assert response.status_code == 401


def test_download_file_without_token():
    _, task_id = create_test_task()

    response = client.get(
        f"/tasks/{task_id}/file"
    )

    assert response.status_code == 401


def test_delete_file_without_token():
    _, task_id = create_test_task()

    response = client.delete(
        f"/tasks/{task_id}/file"
    )

    assert response.status_code == 401


def test_upload_invalid_file_extension():
    token, task_id = create_test_task()

    response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "malicious.exe",
                b"fake executable content",
                "application/octet-stream"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "File type is not allowed"


def test_upload_file_too_large():
    token, task_id = create_test_task()

    large_file = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "large.txt",
                large_file,
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "File size must be 5 MB or less"


def test_user_cannot_access_another_users_file():
    user1_token, task_id = create_test_task()

    upload_response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {user1_token}"
        },
        files={
            "file": (
                "private.txt",
                b"Private file",
                "text/plain"
            )
        }
    )

    assert upload_response.status_code == 200

    user2_token = get_auth_token()

    response = client.get(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {user2_token}"
        }
    )

    assert response.status_code == 404


def test_download_file_after_deletion():
    token, task_id = create_test_task()

    upload_response = client.post(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "delete_then_download.txt",
                b"This file will be deleted",
                "text/plain"
            )
        }
    )

    assert upload_response.status_code == 200

    delete_response = client.delete(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 200

    download_response = client.get(
        f"/tasks/{task_id}/file",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert download_response.status_code == 404