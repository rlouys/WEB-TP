from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form, Response, status
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
    username = request.state.username
    return templates.TemplateResponse("infos.html", {"request": request, "username": username})

@router.get("/unauthorized")
async def protected_route():
    raise HTTPException(status_code=401, detail="Unauthorized access")

# Page 'en construction'
@router.get("/construction", response_class=HTMLResponse)
async def read_play(request: Request):
    username = request.state.username
    return templates.TemplateResponse("construction.html", {"request": request, "username": username})

# Erreur 502
@router.get("/502", response_class=HTMLResponse)
async def read_play(request: Request):
    username = request.state.username
    return templates.TemplateResponse("502.html", {"request": request, "username": username})
