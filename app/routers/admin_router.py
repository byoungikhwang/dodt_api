from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin
from app.dependencies.db_connection import get_db_connection
import asyncpg

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def admin_dashboard(request: Request, user: dict = Depends(get_current_admin), conn: asyncpg.Connection = Depends(get_db_connection)):
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
