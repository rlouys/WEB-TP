from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.model import *
from app.data.dependencies import get_db

from typing import Optional

from app.login_manager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, oauth2_scheme, \
    verify_token, get_user_id_from_token

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

##############
#  LIVRES
##############

# PAGE BIBLIOTHEQUE - GET
@router.get("/liste", response_class=HTMLResponse)
async def liste(request: Request, db: Session = Depends(get_db), page: int = 1):

    user_id = 0
    user_isadmin = 0

    if (getattr(request.state, 'privileges') == "admin"):
        user_isadmin = 1

    # Défini le nombre de livres par page
    per_page = 17
    offset = (page - 1) * per_page

    # Récupère le nombre total de livre
    total_books = db.query(func.count(Livre.id)).scalar()

    # Le nombre de page qu'il y aura en fonction du nombre du livre dans la DB
    total_pages = (total_books + per_page - 1) // per_page

    # Récupère les livres de la première page
    livres_page = db.query(Livre).offset(offset).limit(per_page).all()

    url_context = {
        "request": request,
        "livres": livres_page,
        "page": page,
        "total_pages": total_pages,
        "length": total_books,
        "user_id": user_id,
        "user_isadmin": user_isadmin,
        "is_authenticated": request.state.is_authenticated,
        "privileges": getattr(request.state, 'privileges', 'Utilisateur'),
        "username": request.state.username
    }

    return templates.TemplateResponse("liste.html", url_context)

############################################################################################################################################

# PAGE QUI PERMET DE MODIFIER UN LIVRE
@router.post("/liste", response_class=HTMLResponse)
async def modifier_livre(request: Request,
                         db: Session = Depends(get_db),
                         id: int = Form(...),
                         nom: str = Form(...),
                         auteur: str = Form(...),
                         editeur: str = Form(...),
                         prix: float = Form(...),
                         stock: int = Form(...)
                         ):
    # On récupère le livre à modifier
    livre = db.query(Livre).filter(Livre.id == id).first()

    # S'il n'existe pas de livre, renvoie une erreur 404
    if not livre:
        raise HTTPException(status_code=404, detail="Livre not found")

    # Modification des données du livre en cours dans la DB
    livre.nom = nom
    livre.auteur = auteur
    livre.editeur = editeur
    livre.price = prix
    livre.stock = stock

    db.commit()

    # Redirect back to the book list
    response = RedirectResponse(url="/liste", status_code=303)
    return response


############################################################################################################################################

# Page permettant de modifier un livre
@router.get("/modifier", response_class=HTMLResponse, name="modifier")
async def modifier(request: Request, id: int, db: Session = Depends(get_db)):

    is_authenticated = request.state.is_authenticated
    if not is_authenticated:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    # Récupération du livre
    livre = db.query(Livre).filter(Livre.id == id).first()

    # S'il existe un livre, alors renvoie modifier.html avec les informations du livre en cours
    if livre:
        max_id = db.query(func.max(Livre.id)).scalar() or 0
        return templates.TemplateResponse("modifier.html", {"request": request,
                                                            "livre": livre,
                                                            "max_id": max_id,
                                                            "is_authenticated": request.state.is_authenticated,
                                                            "privileges": getattr(request.state, 'privileges','Utilisateur'),
                                                            "username": request.state.username
                                                            })
    # S'il n'existe pas de livre, renvoie l'erreur 404
    return templates.TemplateResponse("404.html", {"request": request,
                                                   "is_authenticated": request.state.is_authenticated,
                                                   "privileges": getattr(request.state, 'privileges', 'Utilisateur'),
                                                   "username": request.state.username
                                                   })

############################################################################################################################################

# Page permettant de supprimer un livre.
@router.post("/supprimer", response_class=HTMLResponse, name="supprimer")
async def supprimer_livre(response: Response, id: int = Form(...), db: Session = Depends(get_db)):

    # Récupération du livre a supprimer
    livre_to_delete = db.query(Livre).filter(Livre.id == id).first()

    # Si ce livre existe, on le supprime
    if livre_to_delete:
        db.delete(livre_to_delete)
        db.commit()

    return RedirectResponse(url="/liste", status_code=303)

############################################################################################################################################

# Page permettant d'ajouter un nouveau livre - GET
@router.get("/ajouter", response_class=HTMLResponse, name="ajouter")
async def ajouter_livre(request: Request):

    return templates.TemplateResponse("ajouter.html",{"request": request,
                                                      "is_authenticated": request.state.is_authenticated,
                                                      "privileges": getattr(request.state, 'privileges', 'Utilisateur'),
                                                      "username": request.state.username
                                                      })


############################################################################################################################################
@router.post("/ajouter", response_class=HTMLResponse, name="ajouter_post")
async def ajouter_livre(request: Request, db: Session = Depends(get_db), price: str = Form(...), nom: str = Form(...), auteur: str = Form(...),
                        editeur: str = Form(...), boolContinue: Optional[str] = Form(None)):

    # Récupération du Token
    token = request.cookies.get('access_token')
    # On enlève 'bearer'
    token = token[7:]
    # On récupère l'id de l'utilisateur via un decryptage du token
    user_id_from_cookies = get_user_id_from_token(token)

    # On vérifie que le prix du livre est correctement formatté, sinon on renvoie une erreur 400
    normalized_price = price.replace(',', '.')
    try:
        formatted_price = float(normalized_price)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid price format")


    # Création de la nouvelle instance de Livre
    new_livre = Livre(nom=nom,
                      auteur=auteur,
                      editeur=editeur,
                      stock=1,
                      price = formatted_price,
                      created_by = user_id_from_cookies,
                      modified_by = user_id_from_cookies,
                      owner_id = user_id_from_cookies)

    # On ajoute ce livre dans la DB
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)

    # Gère le bouton "continuer" depuis la page ajouter, afin d'ajouter un livre supplémentaire
    if boolContinue == "true":
        return RedirectResponse(url="/ajouter", status_code=303)
    else:
        return RedirectResponse(url="/liste", status_code=303)

