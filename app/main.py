# LIBRARIES
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # import staticfiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Router
from sqlalchemy.orm import Session
from typing import Optional

from .login_manager import login_manager
# FILES
from .model import *
from .dependencies import get_db
from .routes.users import pwd_context
from .schemas import UserSchema

# Variables pour l'authentification
SECRET_KEY="me5GjOLMAQDzFBijhZ9NosTNlkS0J5SH"
ALGORITHM="HS256"

# Initialisation obligatoire de l'application et des routeurs
app = FastAPI()
router = APIRouter()
url_router = Router()


# Ajout des fichiers et liens nécessaires
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


##############
# ROOT
##############

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("index.html", {"request": request})

##############
# LIVRES
##############


# PAGE BIBLIOTHEQUE - GET
@app.get("/liste", response_class=HTMLResponse)
async def liste(request: Request, db: Session = Depends(get_db), page: int = 1):
    per_page = 5
    offset = (page - 1) * per_page

    # Query to get total number of books
    total_books = db.query(func.count(Livre.id)).scalar()
    total_pages = (total_books + per_page - 1) // per_page

    # Query to get books for the current page
    livres_page = db.query(Livre).offset(offset).limit(per_page).all()

    url_context = {
        "request": request,
        "livres": livres_page,
        "page": page,
        "total_pages": total_pages,
        "length": total_books
    }
    return templates.TemplateResponse("liste.html", url_context)


# PAGE MODIFIER LIVRE - POST
@app.post("/liste", response_class=HTMLResponse)
async def modifier_livre(request: Request, db: Session = Depends(get_db), id: int = Form(...), nom: str = Form(...), auteur: str = Form(...), editeur: str = Form(...)):
    # Fetch the book from the data
    livre = db.query(Livre).filter(Livre.id == id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre not found")

    # Update the book details
    livre.nom = nom
    livre.auteur = auteur
    livre.editeur = editeur
    db.commit()

    # Redirect back to the book list
    response = RedirectResponse(url="/liste", status_code=303)
    return response


############################################################################################################################################

# Page permettant de modifier une énigme (à modifier par un pop-up)
@app.get("/modifier", response_class=HTMLResponse, name="modifier")
async def modifier(request: Request, id: int, db: Session = Depends(get_db)):
    # Query for the specific book by ID
    livre = db.query(Livre).filter(Livre.id == id).first()

    # If the book is found, render the modification page with the book's details
    if livre:
        max_id = db.query(func.max(Livre.id)).scalar() or 0
        return templates.TemplateResponse("modifier.html", {"request": request,
                                                            "livre": livre,
                                                            "max_id": max_id })

    # If the book is not found, render a 404 page
    return templates.TemplateResponse("404.html", {"request": request})

############################################################################################################################################

# Page permettant de supprimer un livre.
@app.post("/supprimer", response_class=HTMLResponse, name="supprimer")
async def supprimer_livre(response: Response, id: int = Form(...), db: Session = Depends(get_db)):
    # Query for the specific book by ID and delete it
    livre_to_delete = db.query(Livre).filter(Livre.id == id).first()
    if livre_to_delete:
        db.delete(livre_to_delete)
        db.commit()

    return RedirectResponse(url="/liste", status_code=303)

############################################################################################################################################

# Page permettant d'ajouter un nouveau livre - GET
@app.get("/ajouter", response_class=HTMLResponse, name="ajouter")
async def ajouter_livre(request: Request):

    return templates.TemplateResponse("ajouter.html",{"request": request})


@app.post("/ajouter", response_class=HTMLResponse, name="ajouter_post")
async def ajouter_livre(request: Request, db: Session = Depends(get_db), nom: str = Form(...), auteur: str = Form(...),
                        editeur: str = Form(...), boolContinue: Optional[str] = Form(None)):
    # Create new Livre instance
    new_livre = Livre(nom=nom, auteur=auteur, editeur=editeur, created_by = 1, modified_by = 1)

    # Add to the data
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)  # Refresh to get the ID if needed elsewhere

    print("boolContinue : " + str(boolContinue))
    if boolContinue == "true":
        return RedirectResponse(url="/ajouter", status_code=303)
    else:
        return RedirectResponse(url="/liste", status_code=303)


##############
# USERS
##############

# Page de connexion
@app.get("/connexion", response_class=HTMLResponse, name="connexion")
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})


@app.post("/connexion")
async def handle_connexion(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        return templates.TemplateResponse("connexion.html", {
            "request": response.request,
            "error": "Invalid username or password"
        }, status_code=status.HTTP_401_UNAUTHORIZED)

    access_token = login_manager.create_access_token(data={'sub': user.username})
    login_manager.set_cookie(response, access_token)
    return RedirectResponse(url="/profil", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/inscription", response_class=HTMLResponse)
async def inscription(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/inscription")
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

@app.get("/protected")
async def read_protected(user: UserSchema = Depends(login_manager)):
    return {"message": "Hello, Protected World!"}

############################################################################################################################################


# Page de profil de l'utilisateur
@app.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request):
    return templates.TemplateResponse("profil.html", {"request": request})


##############
# AUTRES PAGES
##############

# Page d'informations
@app.get("/infos", response_class=HTMLResponse, name = "infos")
async def infos(request: Request):
    return templates.TemplateResponse("infos.html", {"request": request})

# Page 'en construction'
@app.get("/construction", response_class=HTMLResponse)
async def read_play(request: Request):
    return templates.TemplateResponse("construction.html", {"request": request})

# Erreur 502
@app.get("/502", response_class=HTMLResponse)
async def read_play(request: Request):
    return templates.TemplateResponse("502.html", {"request": request})

##############
# PAGES D'ERREUR
##############

# ERREURS
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # ERREUR 404 (Page not found)
    if exc.status_code == 404:
        requested_path = request.url.path # On récupère le lien qui a été tenté afin de dire qu'il n'existe pas.
        return templates.TemplateResponse("404.html", {"request": request, "requested": requested_path}, status_code=404)
    if exc.status_code == 502:
        return templates.TemplateResponse("502.html", {"request": request})
    return templates.TemplateResponse("construction.html", {"request": request, "detail": exc.detail}, status_code=exc.status_code)


##############
# ROUTEUR
##############

app.include_router(router)

