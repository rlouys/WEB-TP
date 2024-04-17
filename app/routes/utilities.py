from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
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

# used to create fake books and users
faker = Faker()


# Empty the livres table
@router.get("/empty_livres", response_class=HTMLResponse)
async def empty_livres(db: Session = Depends(get_db)):
    try:
        # Delete all records from the livres table
        db.query(Livre).delete()
        db.commit()
        return RedirectResponse(url="/liste", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate_random_books", response_class=JSONResponse)
async def generate_random_books(request: Request, db: Session = Depends(get_db)):
        token = request.cookies.get('access_token')

        if token is None:
            return JSONResponse(status_code=401, content={"error": "Authentication required"})
        else:
            try:

                token = token[7:]
                # Get current user from token id
                user_id_from_cookies = get_user_id_from_token(token)

                # Generate random book details using Faker
                book_names = [faker.catch_phrase() for _ in range(10)]
                authors = [faker.name() for _ in range(10)]
                publishers = [faker.company() for _ in range(10)]
                prices = [faker.pyfloat(positive=True, min_value=10, max_value=100, right_digits=2) for _ in
                          range(10)]  # Random price between 10 and 100 with 2 decimal places

                # Insert the generated random books into the database
                books = []
                for i in range(10):
                    livre = Livre(
                        nom=book_names[i],
                        auteur=authors[i],
                        editeur=publishers[i],
                        price=prices[i],
                        stock=1,  # Set stock to 1
                        created_by=user_id_from_cookies,  # Set the user ID who created the book
                        modified_by=user_id_from_cookies,  # Set the user ID who last modified the book
                        owner_id=user_id_from_cookies  # Set the user ID who owns the book
                    )
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







# Empty the user table
@router.get("/empty_user_keep_admin", response_class=HTMLResponse)
async def empty_user_keep_admin(db: Session = Depends(get_db)):
    try:
        # Delete all records from the livres table
        db.query(User).filter(User.privileges != "admin").delete(synchronize_session=False)
        db.commit()
        return RedirectResponse(url="/userlist", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate_random_user", response_class=JSONResponse)
async def generate_random_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get('access_token')

    if token is None:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})

    token = token[7:]  # Assuming the token starts with 'Bearer '
    user_id_from_cookies = get_user_id_from_token(token)
    user = db.query(User).filter(User.id == user_id_from_cookies).first()

    if user.privileges != "admin":
        return JSONResponse(status_code=403, content={"error": "Only admins can perform this action"})

    try:
        users = []
        password = "Password123"
        privileges = "user"
        is_locked = False
        hashed_password = generate_password_hash(password)

        for _ in range(5):
            username = faker.user_name()
            email = faker.email()

            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                privileges=privileges,
                is_locked=is_locked
            )
            db.add(new_user)
            users.append({
                "username": username,
                "email": email,
                "password": hashed_password,
                "privileges": privileges,
                "is_locked": is_locked
            })

        db.commit()
        print("TEST")
        return users
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal server error: " + str(e)})

