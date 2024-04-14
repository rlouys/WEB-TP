from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from app import login_manager
from app.login_manager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, oauth2_scheme, \
    verify_token, get_user_id_from_token
from app.model import *
from app.data.dependencies import get_db

from typing import Optional
from app.schemas import UserSchema
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

##############
# USERS
##############


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Vérifiez si l'utilisateur est récupéré correctement
    if user:
        logger.info(f"Nom d'utilisateur: {user.username}")  # Affiche le nom d'utilisateur dans la console
    else:
        logger.info("Aucun utilisateur trouvé")

    return templates.TemplateResponse("main.html", {
        "request": request,
        "username": user.username if user else "Utilisateur"
    })


# Page de connexion
@router.get("/connexion", response_class=HTMLResponse, name="connexion")
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})


@router.post("/connexion")
async def handle_connexion(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()
    if user and user.verify_password(form_data.password):
        access_token = create_access_token(data={'sub': user.username, 'id': user.id})
        response = RedirectResponse(url=f"/profil?user_id={user.id}", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, path="/")
        return response
    else:
        # Pas besoin de modifier le statut ici car nous ne renvoyons pas une réponse 401
        return templates.TemplateResponse("connexion.html", {
            "request": request,  # Utilisez request plutôt que response.request
            "error": "Nom d'utilisateur ou mot de passe invalide."
        })  # Le statut par défaut est 200 OK
@router.get("/inscription", response_class=HTMLResponse)
async def inscription(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/inscription")
async def create_user(request: Request, db: Session = Depends(get_db),
                      new_username: str = Form(...), new_email: EmailStr = Form(...),
                      new_password: str = Form(...), confirm_password: str = Form(...)):
    if len(new_password) < 4:
        return render_error_template(request, "signup.html", "Le mot de passe doit contenir au moins 4 caractères.")
    if new_password != confirm_password:
        return render_error_template(request, "signup.html", "Les mots de passe ne correspondent pas.")
    if db.query(User).filter((User.email == new_email) | (User.username == new_username)).first():
        return render_error_template(request, "signup.html", "Email ou nom d'utilisateur déjà utilisé.")

    hashed_password = generate_password_hash(new_password)
    new_user = User(username=new_username, email=new_email, password_hash=hashed_password, privileges="user", is_locked=0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Received data - Username: {new_username}, Email: {new_email}, Password: {new_password}, Confirm: {confirm_password}")
    return templates.TemplateResponse("signup_success.html", {"request": request})


@router.get("/protected")
async def read_protected(user: UserSchema = Depends(get_current_user)):
    return {"message": "Hello, Protected World!"}

############################################################################################################################################

# Page de profil de l'utilisateur
@router.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request, user_id: int, db: Session = Depends(get_db)):


    token = request.cookies.get('access_token')
    token = token[7:]
    # Get current user from token id
    user_id_from_cookies = get_user_id_from_token(token)

    user_data = db.query(User).filter(User.id == user_id).first()

    if user_id != user_id_from_cookies:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")

    if not user_data:
        return templates.TemplateResponse("404.html", {"request": request})

    return templates.TemplateResponse("profil.html", {
        "request": request,
        "user": user_data
    })


@router.post("/update-profile")
async def update_profile(request: Request, db: Session = Depends(get_db),
                         username: Optional[str] = Form(None), email: Optional[str] = Form(None),
                         currentPassword: Optional[str] = Form(None), newPassword: Optional[str] = Form(None),
                         confirmPassword: Optional[str] = Form(None)):
    token = request.cookies.get('access_token', "").split(" ")[1]
    user_id = get_user_id_from_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Utilisateur non trouvé"
        })

    context = {"request": request, "user": user}  # Contexte de base pour le template

    # Vérifications des entrées
    errors = False
    if username:
        existing_username = db.query(User).filter(User.username == username, User.id != user_id).first()
        if existing_username:
            context["error_username"] = "Le nom d'utilisateur est déjà utilisé."
            errors = True

    if email:
        existing_email = db.query(User).filter(User.email == email, User.id != user_id).first()
        if existing_email:
            context["error_email"] = "L'adresse email est déjà employée."
            errors = True

    # Validation pour les changements de mot de passe
    if currentPassword or newPassword or confirmPassword:
        if not currentPassword:
            context["error_current_password"] = "Veuillez entrer votre mot de passe actuel."
            errors = True
        elif not check_password_hash(user.password_hash, currentPassword):
            context["error_current_password"] = "Le mot de passe actuel est incorrect."
            errors = True

        if not newPassword:
            context["error_new_password"] = "Veuillez entrer un nouveau mot de passe."
            errors = True
        elif len(newPassword) < 4:
            context["error_new_password_length"] = "Le nouveau mot de passe doit contenir au moins 4 caractères."
            errors = True

        if not confirmPassword:
            context["error_confirm_password"] = "Veuillez confirmer votre nouveau mot de passe."
            errors = True
        elif newPassword != confirmPassword:
            context["error_new_password_match"] = "Les nouveaux mots de passe ne correspondent pas."
            errors = True

    if errors:
        return templates.TemplateResponse("profil.html", context)

    # Mise à jour des informations valides
    if username:
        user.username = username
    if email:
        user.email = email
    if newPassword:
        user.password_hash = generate_password_hash(newPassword)

    db.commit()
    context["message"] = "Profil mis à jour avec succès."
    return templates.TemplateResponse("profil.html", context)

@router.get("/api/check-username")
async def check_username(username: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return {"is_unique": False}
    return {"is_unique": True}

@router.get("/api/check-email")
async def check_email(email: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return {"is_unique": False}
    return {"is_unique": True}


def render_error_template(request: Request, template_name: str, error_message: str, status_code: int = 400):
    return templates.TemplateResponse(template_name, {
        "request": request,
        "error": error_message  # Utilisez "error" comme clé pour que cela corresponde au template
    }, status_code=status_code)

''' tokens d'identification'''
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username, 'id': user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
