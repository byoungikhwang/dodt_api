from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.dependencies.auth import get_optional_user, get_current_user_or_redirect # Import get_current_user_or_redirect
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def index(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@router.get("/feed")
async def feed_page(request: Request, user: dict = Depends(get_current_user_or_redirect)):
    return templates.TemplateResponse("feed.html", {"request": request, "user": user})

@router.get("/add")
async def add_page(request: Request, user: dict = Depends(get_current_user_or_redirect)):
    return templates.TemplateResponse("add.html", {"request": request, "user": user})

@router.get("/generate-type2")
async def generate_type2_page(request: Request, user: dict = Depends(get_current_user_or_redirect)):
    return templates.TemplateResponse("generate_type2.html", {"request": request, "user": user})

@router.get("/dashboard")
async def dashboard(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
