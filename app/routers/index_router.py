from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.dependencies.auth import get_optional_user, get_current_user_or_redirect
from app.dependencies.db_connection import get_db_connection # Add this import
from app.services.media_service import MediaService
import asyncpg
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

@router.get("/api/media")
async def get_media_feed(
    user: Optional[dict] = Depends(get_optional_user),
    media_service: MediaService = Depends(), # Changed from VideoService
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Returns a list of all media (videos and images) for the main feed.
    """
    current_user_id = int(user["sub"]) if user else None
    media_items = await media_service.get_feed_media(
        conn=conn,
        sort='popular',
        search=None,
        limit=6,
        offset=0,
        current_user_id=current_user_id
    )
    return media_items
