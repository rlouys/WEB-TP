# LIBRARIES
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # User authentication
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # import staticfiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Router
from sqlalchemy.orm import Session
from jose import jwt # user authentication
from datetime import datetime, timedelta
import random
from typing import Optional

# FILES
from .model import *
#from .dependencies import get_db

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


# DB DES LIVRES
livres = [
    {'id': 0, 'nom': 'Le Petit Prince', 'auteur': "Antoine de Saint-Exupéry", 'editeur': 'Gallimard'},
    {'id': 1, 'nom': 'Harry Potter à l\'école des sorciers', 'auteur': "J.K. Rowling", 'editeur': "Gallimard Jeunesse"},
    {'id': 2, 'nom': '1984', 'auteur': "George Orwell", 'editeur': "Secker & Warburg"},
    {'id': 3, 'nom': 'Le Seigneur des anneaux', 'auteur': "J.R.R. Tolkien", 'editeur': "Allen & Unwin"},
    {'id': 4, 'nom': 'Le Grand Meaulnes', 'auteur': "Alain-Fournier", 'editeur': "Éditions Émile-Paul Frères"},
    {'id': 5, 'nom': 'Orgueil et Préjugés', 'auteur': "Jane Austen", 'editeur': "T. Egerton, Whitehall"},
    {'id': 6, 'nom': 'L\'Alchimiste', 'auteur': "Paulo Coelho", 'editeur': "HarperCollins"},
    {'id': 7, 'nom': 'Les Misérables', 'auteur': "Victor Hugo", 'editeur': "A. Lacroix, Verboeckhoven & Cie"},
    {'id': 8, 'nom': 'Crime et Châtiment', 'auteur': "Fiodor Dostoïevski", 'editeur': "The Russian Messenger"},
    {'id': 9, 'nom': 'Le Nom de la rose', 'auteur': "Umberto Eco", 'editeur': "Bompiani"}
]


############################################################################################################################################
# ROOT
############################################################################################################################################

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

############################################################################################################################################
# LIVRES
############################################################################################################################################


# PAGE BIBLIOTHEQUE - GET
@app.get("/liste", response_class=HTMLResponse, name="liste")
async def liste(request: Request,page: int = 1):

    # BACK END POUR LA PAGINATION
    per_page = 5 # nombre de livres par page
    start = (page - 1) * per_page # premier livre à afficher
    end = min(start + per_page, len(livres)) # dernier livre à afficher
    total_pages = (len(livres) + per_page - 1) // per_page # on déduit le nombre de page totales (pour afficher les bons boutons)
    livres_page = livres[start:end] # ensemble de livre qui va être print

    url_context = {"request": request, "livres": livres_page, "page": page, "total_pages": total_pages, "length": len(livres)}
    return templates.TemplateResponse("liste.html", url_context)


# PAGE MODIFIER LIVRE - POST
@app.post("/liste", response_class=HTMLResponse)
async def modifier_livre(request: Request, id: int = Form(...), nom: str = Form(...), auteur: str = Form(...), editeur: str = Form(...)):

    # RECUPERATION DES INFOS MODIFIÉES DU LIVRE
    try:
        livre_data = Livre(id=id, nom=nom, auteur=auteur, editeur=editeur)
    except ValueError as ve:
        print(f"Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    # MODIFICATION DU LIVRE DANS LA DB
    for livre in livres:
        if livre['id'] == int(id):
            livre['nom'] = nom
            livre['auteur'] = auteur
            livre['editeur'] = editeur

    # ON RENVOIE LA BONNE PAGE
    page = 1 # numéro de la page sur laquelle revenir
    per_page = 5 # nombre de livres par page
    start = (page - 1) * per_page # premier livre à afficher
    end = min(start + per_page, len(livres))  # dernier livre à afficher
    total_pages = (len(livres) + per_page - 1) // per_page # on déduit le nombre de page totales (pour afficher les bons boutons)
    livres_page = livres[start:end]  # ensemble de livre qui va être print

    url_context = {"request": request, "livres": livres_page, "page": page, "total_pages": total_pages, "length": len(livres)}
    return templates.TemplateResponse("liste.html", url_context)


############################################################################################################################################

# Page permettant de modifier une énigme (à modifier par un pop-up)
@app.get("/modifier", response_class=HTMLResponse, name="modifier")
async def modifier(request: Request, id: int):

    # On récupère le bon ID de livre, puis on l'envoie au HTML pour qu'ils puissent être mis dans les placeholder.
    for livre in livres:
        if livre['id'] == int(id):
            return templates.TemplateResponse("modifier.html", {"request": request, "livre": livre, "max_id": len(livres)-1})

    return templates.TemplateResponse("404.html", {"request": request})

############################################################################################################################################

# Page permettant de supprimer un livre.
@app.post("/supprimer", response_class=HTMLResponse, name="supprimer")
async def supprimer_livre(response: Response,id : int = Form(...)):
    global livres

    livres = [book for book in livres if book['id'] != id]

    return RedirectResponse(url="/liste", status_code=303)

############################################################################################################################################

# Page permettant d'ajouter un nouveau livre - GET
@app.get("/ajouter", response_class=HTMLResponse, name="ajouter")
async def ajouter_livre(request: Request):

    return templates.TemplateResponse("ajouter.html",{"request": request})

@app.post("/ajouter", response_class=HTMLResponse, name="ajouter_post")
async def ajouter_livre(request: Request, nom: str = Form(...), auteur: str = Form(...), editeur: str = Form(...), boolContinue: Optional[str] = Form(None)):
    global livres

    # L'ID du livre créé est max(existing_id) + 1, s'il n'existe pas de livres, l'id = 0
    new_id = max([livre['id'] for livre in livres]) + 1 if livres else 0
    new_livre = {"id": new_id, "nom":nom, "auteur": auteur, "editeur":editeur}
    livres.append(new_livre)

    print("boolContinue : " + str(boolContinue))
    print(type(boolContinue))
    if boolContinue == "true":
        return RedirectResponse(url="/ajouter", status_code=303)
    else:
        return RedirectResponse(url="/liste", status_code=303)

############################################################################################################################################
# USERS
############################################################################################################################################

# Page de connexion
@app.get("/connexion", response_class=HTMLResponse, name="connexion")
async def connexion(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request})

@app.post("/connexion")
async def handle_connexion(response: Response):
    return RedirectResponse(url="/profil", status_code=status.HTTP_303_SEE_OTHER)

############################################################################################################################################


# Page de profil de l'utilisateur
@app.get("/profil", response_class=HTMLResponse, name="profil")
async def profil(request: Request):
    return templates.TemplateResponse("profil.html", {"request": request})


############################################################################################################################################
# AUTRES PAGES
############################################################################################################################################

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

############################################################################################################################################
# PAGES D'ERREUR
############################################################################################################################################


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


############################################################################################################################################
# ROUTEUR
############################################################################################################################################

app.include_router(router)

