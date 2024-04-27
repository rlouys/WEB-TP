from fastapi import Query, FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import not_

from faker import Faker

from app.model import *
from app.data.dependencies import get_db
from app.login_manager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, oauth2_scheme, \
    verify_token, get_user_id_from_token


##############
# UTILITIES
##############

router = APIRouter()

# Génère l'instance Faker qui va nous permettre de générer des informations random
faker = Faker()

############################################################################################################################################

# Vide la table des livres
@router.get("/empty_livres", response_class=HTMLResponse)
async def empty_livres(db: Session = Depends(get_db)):
    try:
        # Supprime toutes les instances de Livre de la base de données
        db.query(Livre).delete()
        db.commit()
        return RedirectResponse(url="/liste", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

############################################################################################################################################

@router.get("/generate_random_books", response_class=JSONResponse)
async def generate_random_books(request: Request, db: Session = Depends(get_db), count: int = Query(10, gt=0, le=100)):
        token = request.cookies.get('access_token')

        # L'authentification est requise pour générer des livres, et l'utilisateur doit être admin pour que les boutons apparaissent
        if token is None:
            return JSONResponse(status_code=401, content={"error": "Authentication required"})
        else:
            try:

                token = token[7:]
                # Get current user from token id
                user_id_from_cookies = get_user_id_from_token(token)

                # Liste de livres
                books = []

                # Génération de n Livres avec FAKER
                for _ in range(count):
                    username = faker.user_name()
                    email = faker.email()
                    book_name = faker.catch_phrase()
                    author = faker.name()
                    publisher = faker.company()
                    price = faker.pyfloat(positive=True, min_value=5, max_value=45, right_digits=2)

                    # Création de l'instance
                    livre = Livre(
                        nom=book_name,
                        auteur=author,
                        editeur=publisher,
                        price=price,
                        stock=1,
                        created_by=user_id_from_cookies,
                        modified_by=user_id_from_cookies,
                        owner_id=user_id_from_cookies
                    )

                    # Ajout de l'instance
                    db.add(livre)

                    books.append({
                        "nom": livre.nom,
                        "auteur": livre.auteur,
                        "editeur": livre.editeur,
                        "price": livre.price
                    })

                db.commit()
                return books
            except Exception as e:
                return {"error": str(e)}

############################################################################################################################################
# Vide la table des utilisateurs
@router.get("/empty_user_keep_admin", response_class=HTMLResponse)
async def empty_user_keep_admin(db: Session = Depends(get_db)):
    try:
        # Suppression de toutes les instances de la table, sauf les ADMINs
        db.query(User).filter(User.privileges != "admin").delete(synchronize_session=False)
        db.commit()
        return RedirectResponse(url="/userlist", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


############################################################################################################################################
# CREATION DE USER RANDOM
@router.get("/generate_random_user", response_class=JSONResponse)
async def generate_random_user(request: Request, db: Session = Depends(get_db), count: int = Query(5, gt=0, le=100)):
    token = request.cookies.get('access_token')

    if token is None:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})

    token = token[7:]  # Assuming the token starts with 'Bearer '
    user_id_from_cookies = get_user_id_from_token(token)
    user = db.query(User).filter(User.id == user_id_from_cookies).first()

    if user.privileges != "admin":
        return JSONResponse(status_code=403, content={"error": "Only admins can perform this action"})

    try:
        # Tous les User générés auront comme mot de passe "Password123" et comme privileges "user", et ne seront pas bloqués.
        users = []
        password = "Password123"
        privileges = "user"
        is_locked = False
        hashed_password = generate_password_hash(password)

        for _ in range(count):
            # génération des fake Users
            username = faker.user_name()
            email = faker.email()
            name = faker.name()
            firstname = faker.first_name()

            # Création de l'instance de User
            new_user = User(
                username=username,
                email=email,
                name=name,
                firstname=firstname,
                password_hash=hashed_password,
                privileges=privileges,
                is_locked=is_locked
            )

            # Ajout de l'utilisateur
            db.add(new_user)

            # Ajout de l'utilisateur dans la liste
            users.append({
                "username": username,
                "email": email,
                "name": name,
                "firstname": firstname,
                "password": hashed_password,
                "privileges": privileges,
                "is_locked": is_locked
            })

        db.commit()
        return users
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal server error: " + str(e)})

