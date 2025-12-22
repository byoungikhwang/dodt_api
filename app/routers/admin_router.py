from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin, get_current_admin_or_redirect
from app.dependencies.db_connection import get_db_connection
import asyncpg

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def admin_dashboard(request: Request, user: dict = Depends(get_current_admin_or_redirect), conn: asyncpg.Connection = Depends(get_db_connection)):
    # Fetch stats
    users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
    
    # Fetch members
    members = await conn.fetch("SELECT * FROM users ORDER BY id DESC LIMIT 50")
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user,
        "users_count": users_count,
        "members": members
    })

@router.get("/users", response_model=list[dict])
async def get_all_users(user: dict = Depends(get_current_admin_or_redirect), conn: asyncpg.Connection = Depends(get_db_connection)):
    """
    Returns a list of all users. Accessible only by admins.
    """
    users = await conn.fetch("SELECT id, email, name, custom_id, role, credits, created_at FROM users ORDER BY id ASC")
    return [dict(user) for user in users]

@router.get("/videos")
async def video_management_page(request: Request, user: dict = Depends(get_current_admin_or_redirect)):
    """Serves the video management page for admins."""
    return templates.TemplateResponse("admin_videos.html", {"request": request, "user": user})
