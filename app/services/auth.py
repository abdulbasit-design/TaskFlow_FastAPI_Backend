from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.jwt import create_access_token
from app.utils.password import hash_password, verify_password


def register_user(
    db: Session,
    user_data: UserCreate
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        return None

    hashed_password = hash_password(
        user_data.password
    )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    user_data: UserLogin
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        return None

    password_valid = verify_password(
        user_data.password,
        user.password
    )

    if not password_valid:
        return None

    token_data = {
        "user_id": user.id,
        "email": user.email
    }

    access_token = create_access_token(
        token_data
    )

    return access_token