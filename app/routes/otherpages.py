from fastapi import FastAPI, Request, APIRouter, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


##############
# AUTRES PAGES
##############

# Page d'informations
@router.get("/infos", response_class=HTMLResponse, name = "infos")
async def infos(request: Request):
    return templates.TemplateResponse("infos.html", {"request": request})

# Page 'en construction'
@router.get("/construction", response_class=HTMLResponse)
async def read_play(request: Request):
    return templates.TemplateResponse("construction.html", {"request": request})

# Erreur 502
@router.get("/502", response_class=HTMLResponse)
async def read_play(request: Request):
    return templates.TemplateResponse("502.html", {"request": request})
