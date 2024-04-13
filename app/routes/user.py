from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app import login_manager
from app.login_manager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, oauth2_scheme, \
    verify_token
from app.model import *
from app.data.dependencies import get_db

from typing import Optional
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


def set_cookie(response: Response, access_token: str):
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

@router.post("/connexion")
async def handle_connexion(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()
    if user and user.verify_password(form_data.password):
        access_token = create_access_token(data={'sub': user.username})
        set_cookie(response, access_token)
        response = RedirectResponse(url=f"/profil?user_id={user.id}", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, path="/")
        return response
    else:
        return templates.TemplateResponse("connexion.html", {
            "request": response.request,  # Ensure to pass request not response
            "error": "Invalid username or password"
        }, status_code=status.HTTP_401_UNAUTHORIZED)




@router.get("/inscription", response_class=HTMLResponse)
async def inscription(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/inscription")
async def create_user(request: Request, db: Session = Depends(get_db),
                      new_username: str = Form(...), new_email: EmailStr = Form(...),
                      new_password: str = Form(...), confirm_password: str = Form(...)):
    if new_password != confirm_password:
        return render_error_template(request, "signup.html", "Les mots de passe ne correspondent pas.")
    if db.query(User).filter((User.email == new_email) | (User.username == new_username)).first():
        return render_error_template(request, "signup.html", "Email ou nom d'utilisateur déjà utilisé.")

    hashed_password = generate_password_hash(new_password)  # Hashage du mot de passe
    new_user = User(username=new_username, email=new_email, password_hash=hashed_password)  # Utilisez password_hash ici
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse("signup_success.html", {"request": request})

@router.get("/protected")
async def read_protected(user: UserSchema = Depends(get_current_user)):
    return {"message": "Hello, Protected World!"}

############################################################################################################################################


@router.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Utilisation de l'utilisateur authentifié pour accéder à ses données
    user_data = db.query(User).filter(User.id == user.id).first()
    if not user_data:
        return templates.TemplateResponse("404.html", {"request": request})

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "user": user_data
    })
@router.post("/change-password", response_class=HTMLResponse)
async def change_password(request: Request, db: Session = Depends(get_db), user_id: int = Depends(get_current_user),
                          currentPassword: str = Form(...), newPassword: str = Form(...), confirmPassword: str = Form(...)):
    # Chargement de l'utilisateur à partir de la base de données
    user_data = db.query(User).filter(User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérification du mot de passe actuel
    if not check_password_hash(user_data.password_hash, currentPassword):
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Le mot de passe actuel est incorrect."
        })

    # Vérification de la correspondance des nouveaux mots de passe
    if newPassword != confirmPassword:
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Les nouveaux mots de passe ne correspondent pas."
        })

    # Mise à jour du mot de passe dans la base de données
    try:
        user_data.password_hash = generate_password_hash(newPassword)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du mot de passe")

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "message": "Mot de passe mis à jour avec succès."
    })

def render_error_template(request: Request, template_name: str, error_message: str,
                          status_code: int = 400):
    return templates.TemplateResponse(template_name, {
        "request": request,
        "error_message": error_message
    }, status_code=status_code)

@router.post("/inscription")
async def create_user(request: Request, db: Session = Depends(get_db),
                      new_username: str = Form(...), new_email: EmailStr = Form(...),
                      new_password: str = Form(...), confirm_password: str = Form(...)):
    # Vérifier si les mots de passe sont identiques
    if new_password != confirm_password:
        return render_error_template(request, "signup.html", "Les mots de passe ne correspondent pas.")

    # Vérifier si l'email ou le nom d'utilisateur est déjà utilisé
    if db.query(User).filter((User.email == new_email) | (User.username == new_username)).first():
        return render_error_template(request, "signup.html", "Email ou nom d'utilisateur déjà utilisé.")

    # Hasher le nouveau mot de passe
    hashed_password = generate_password_hash(new_password)

    # Créer le nouvel utilisateur
    new_user = User(username=new_username, email=new_email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Réponse en cas de succès
    return templates.TemplateResponse("signup_success.html", {"request": request})

''' tokens d'identification'''
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

