from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.login_manager import create_access_token, get_current_user, oauth2_scheme, \
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

# Page de connexion
@router.get("/connexion", response_class=HTMLResponse, name="connexion")
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})


@router.post("/connexion")
async def handle_connexion(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()
    if user and user.verify_password(form_data.password):
        try:
            # Créer un token avec toutes les données critiques
            access_token = create_access_token(data={
                'sub': user.username,
                'id': user.id,
                'privileges': user.privileges,
                'is_locked': str(user.is_locked)  # Stocker comme string car il s'agit d'un booléen
            })
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            # Stocker uniquement le access_token dans les cookies
            response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, secure=True,
                                samesite='Lax')
            response.set_cookie(key="is_authenticated", value="true", httponly=True, secure=True, samesite='Lax')

            return response
        except Exception as e:
            logging.error(f"Failed to create access token: {str(e)}")
            return templates.TemplateResponse("connexion.html", {
                "request": request,
                "error": "Erreur interne du serveur."
            })
    else:
        return templates.TemplateResponse("connexion.html", {
            "request": request,
            "error": "Nom d'utilisateur ou mot de passe invalide."
        })


@router.get("/deconnexion")
async def deconnexion(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("is_authenticated", path="/")

    return response


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
    new_user = User(username=new_username, email=new_email, password_hash=hashed_password, privileges="user",
                    is_locked=0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(
        f"Received data - Username: {new_username}, Email: {new_email}, Password: {new_password}, Confirm: {confirm_password}")
    return templates.TemplateResponse("signup_success.html", {"request": request})


@router.get("/protected")
async def read_protected(user: UserSchema = Depends(get_current_user)):
    return {"message": "Hello, Protected World!"}


############################################################################################################################################

# Page de profil de l'utilisateur
@router.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    if not user:
        return templates.TemplateResponse("404.html", {"request": request, "error": "Profil non trouvé"})

        # Aucun besoin de vérifier le token ou d'extraire l'ID de l'utilisateur, tout est géré par `get_current_user`
    return templates.TemplateResponse("profil.html", {
            "request": request,
            "username": user.username,
            "user": user
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
        logger.error("User not found with ID: %s", user_id)
        return templates.TemplateResponse("profil.html", {
            "request": request,
            "error": "Utilisateur non trouvé"
        })

    context = {"request": request, "user": user, "username": username if username else user.username}

    # Vérification des entrées et gestion des erreurs
    errors = False
    if username and username != user.username:
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            context["error_username"] = "Le nom d'utilisateur est déjà utilisé."
            errors = True

    if email and email != user.email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            context["error_email"] = "L'adresse email est déjà employée."
            errors = True

    if newPassword or confirmPassword:
        if not currentPassword:
            context["error_current_password"] = "Veuillez entrer votre mot de passe actuel."
            errors = True
        elif not check_password_hash(user.password_hash, currentPassword):
            context["error_current_password"] = "Le mot de passe actuel est incorrect."
            errors = True
        if newPassword != confirmPassword:
            context["error_new_password_match"] = "Les nouveaux mots de passe ne correspondent pas."
            errors = True
        if len(newPassword) < 4:
            context["error_new_password_length"] = "Le nouveau mot de passe doit contenir au moins 4 caractères."
            errors = True

    if errors:
        return templates.TemplateResponse("profil.html", context)

    # Mise à jour des informations valides
    updated = False
    if username and username != user.username:
        user.username = username
        updated = True
    if email and email != user.email:
        user.email = email
        updated = True
    if newPassword and check_password_hash(user.password_hash, currentPassword):
        user.password_hash = generate_password_hash(newPassword)
        updated = True

    if updated:
        db.commit()
        # Créer un nouveau token JWT avec les données mises à jour
        new_token_data = {
            'sub': user.username,
            'id': user.id,
            'privileges': user.privileges,
            'is_locked': str(user.is_locked)
        }
        new_token = create_access_token(data=new_token_data)
        # Mettre à jour le cookie avec le nouveau token
        response = templates.TemplateResponse("profil.html", {
            "request": request,
            "message": "Profil mis à jour avec succès.",
            "user": user  # Assurez-vous que l'objet user est correctement passé ici
        })
        response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, secure=True, samesite='Lax')
        return response

    # Si aucune mise à jour n'est effectuée, retournez également l'utilisateur pour éviter 'user' is undefined
    return templates.TemplateResponse("profil.html", {
        "request": request,
        "message": "Aucune modification nécessaire.",
        "user": user  # Assurez-vous que l'objet user est correctement passé ici également
    })

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
