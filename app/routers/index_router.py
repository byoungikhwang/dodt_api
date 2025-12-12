from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.dependencies.auth import get_optional_user
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def index(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@router.get("/dashboard")
async def dashboard(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
