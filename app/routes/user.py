from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from app.model import *
from app.data.dependencies import get_db

from typing import Optional

from app.login_manager import login_manager
from app.schemas import UserSchema

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

##############
# USERS
##############

# Page de connexion
@router.get("/connexion", response_class=HTMLResponse, name="connexion")
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})


@router.post("/connexion")
async def handle_connexion(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()
    if user and pwd_context.verify(form_data.password, user.password_hash):
        access_token = login_manager.create_access_token(data={'sub': user.username})
        login_manager.set_cookie(response, access_token)
        return RedirectResponse(url=f"/profil?user_id={user.id}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse("connexion.html", {
            "request": response,
            "error": "Invalid username or password"
        }, status_code=status.HTTP_401_UNAUTHORIZED)

@router.get("/inscription", response_class=HTMLResponse)
async def inscription(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/inscription")
async def create_user(request: Request, db: Session = Depends(get_db),
                      new_username: str = Form(...), new_email: EmailStr = Form(...),
                      new_password: str = Form(...), confirm_password: str = Form(...)):
    # vérif si les mdp sont identiquues
    if new_password != confirm_password:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error_message": "Les mots de passe ne correspondent pas."
        })
    #verif si présent
    user = db.query(User).filter((User.email == new_email) | (User.username == new_username)).first()
    if user:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error_message": "Email ou nom d'utilisateur déjà utilisé."
        })

    #hashage
    hashed_password = pwd_context.hash(new_password)
    new_user = User(
        username=new_username,
        email=new_email,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse("signup_succes.html", {"request": request})

@router.get("/protected")
async def read_protected(user: UserSchema = Depends(login_manager)):
    return {"message": "Hello, Protected World!"}

############################################################################################################################################


# Page de profil de l'utilisateur
@router.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request, user_id: int, db: Session = Depends(get_db)):
    user_data = db.query(User).filter(User.id == user_id).first()
    if not user_data:
        return templates.TemplateResponse("404.html", {"request": request})

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "user": user_data
    })

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(request: Request, db: Session = Depends(get_db), user: UserSchema = Depends(login_manager),
                          currentPassword: str = Form(...), newPassword: str = Form(...), confirmPassword: str = Form(...)):
    user_data = db.query(User).filter(User.username == user.username).first()
    if not user_data or not pwd_context.verify(currentPassword, user_data.password_hash):
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Le mot de passe actuel est incorrect."
        })

    if newPassword != confirmPassword:
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Les nouveaux mots de passe ne correspondent pas."
        })

    user_data.password_hash = pwd_context.hash(newPassword)
    db.commit()

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "message": "Mot de passe mis à jour avec succès."
    })
