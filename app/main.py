# LIBRARIES
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # import staticfiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Router
from sqlalchemy.orm import Session

from .login_manager import create_access_token, oauth2_scheme, verify_token
# FILES
from .model import *
from app.data.dependencies import get_db


from app.routes import utilities, livres, user, otherpages

# Initialisation obligatoire de l'application et des routeurs
app = FastAPI()
router = APIRouter()
url_router = Router()

# Ajout des fichiers et liens nécessaires
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Autres routes

app.include_router(utilities.router)
app.include_router(livres.router)
app.include_router(user.router)
app.include_router(otherpages.router)

##############
# ROOT
##############


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):

    return templates.TemplateResponse("index.html", {"request": request})



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
    if exc.status_code == 401:
        return templates.TemplateResponse("unauthorized.html", {"request": request})
    return templates.TemplateResponse("construction.html", {"request": request, "detail": exc.detail}, status_code=exc.status_code)



##############
# ROUTEUR
##############

app.include_router(router)
