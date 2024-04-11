from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.login_manager import login_manager
from app.model import User
from app.services.users import get_user_by_username, get_user_by_email
from app.schemas import UserSchema

router = APIRouter(prefix="/users")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
def login_route(
        username: Annotated[str, Body()],
        password: Annotated[str, Body()],
        email: Annotated[str, Body()],
):
    # Vérifier si l'entrée est un email
    if "@" in username:
        user = get_user_by_email(email)
    else:
        user = get_user_by_username(username)

    if user is None or not user.password == password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad credentials."
        )
    access_token = login_manager.create_access_token(
        data={'sub': user.id}
    )

    response = JSONResponse({"status": "success"})
    response.set_cookie(
        key=login_manager.cookie_name,
        value=access_token,
        httponly=True
    )
    return response


@router.post('/logout')
def logout_route():
    response = JSONResponse({'status': 'success'})
    response.delete_cookie(
        key=login_manager.cookie_name,
        httponly=True
    )
    return response


@router.get("/me")
def current_user_route(
        user: UserSchema = Depends(login_manager),
):
    return user

@router.post("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

