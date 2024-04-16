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
# LIVRES
##############


# PAGE BIBLIOTHEQUE - GET
@router.get("/liste", response_class=HTMLResponse)
async def liste(request: Request, db: Session = Depends(get_db), page: int = 1):

    user_id = 0
    user_name = ''
    user_isadmin = 0

    token = request.cookies.get('access_token')

    if token:
        token = token[7:]

        if verify_token(token):
            user_id = get_user_id_from_token(token)
            userFromToken = db.query(User).filter(User.id == user_id).first()
            user_name = userFromToken.username
            if (userFromToken.privileges == 'admin'):
                user_isadmin = 1


    per_page = 10
    offset = (page - 1) * per_page

    # Query to get total number of books
    total_books = db.query(func.count(Livre.id)).scalar()
    total_pages = (total_books + per_page - 1) // per_page

    # Query to get books for the current page
    livres_page = db.query(Livre).offset(offset).limit(per_page).all()

    print(user_isadmin)

    url_context = {
        "request": request,
        "livres": livres_page,
        "page": page,
        "total_pages": total_pages,
        "length": total_books,
        "user_id": user_id,
        "username": user_name,
        "user_isadmin": user_isadmin
    }

    return templates.TemplateResponse("liste.html", url_context)


# PAGE MODIFIER LIVRE - POST
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
    # Fetch the book from the data
    livre = db.query(Livre).filter(Livre.id == id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre not found")

    # Update the book details
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

# Page permettant de modifier une énigme (à modifier par un pop-up)
@router.get("/modifier", response_class=HTMLResponse, name="modifier")
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
@router.post("/supprimer", response_class=HTMLResponse, name="supprimer")
async def supprimer_livre(response: Response, id: int = Form(...), db: Session = Depends(get_db)):
    # Query for the specific book by ID and delete it
    livre_to_delete = db.query(Livre).filter(Livre.id == id).first()
    if livre_to_delete:
        db.delete(livre_to_delete)
        db.commit()

    return RedirectResponse(url="/liste", status_code=303)

############################################################################################################################################

# Page permettant d'ajouter un nouveau livre - GET
@router.get("/ajouter", response_class=HTMLResponse, name="ajouter")
async def ajouter_livre(request: Request):

    return templates.TemplateResponse("ajouter.html",{"request": request})


@router.post("/ajouter", response_class=HTMLResponse, name="ajouter_post")
async def ajouter_livre(request: Request, db: Session = Depends(get_db), price: str = Form(...), nom: str = Form(...), auteur: str = Form(...),
                        editeur: str = Form(...), boolContinue: Optional[str] = Form(None)):

    token = request.cookies.get('access_token')
    token = token[7:]
    # Get current user from token id
    user_id_from_cookies = get_user_id_from_token(token)
    print(user_id_from_cookies)
    # Ensure price is well-formatted
    normalized_price = price.replace(',', '.')
    try:
        formatted_price = float(normalized_price)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid price format")

    # Create new Livre instance
    new_livre = Livre(nom=nom, auteur=auteur, editeur=editeur, price = formatted_price, created_by = user_id_from_cookies, modified_by = user_id_from_cookies, owner_id = user_id_from_cookies)

    # Add to the data
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)  # Refresh to get the ID if needed elsewhere

    print("boolContinue : " + str(boolContinue))
    if boolContinue == "true":
        return RedirectResponse(url="/ajouter", status_code=303)
    else:
        return RedirectResponse(url="/liste", status_code=303)

