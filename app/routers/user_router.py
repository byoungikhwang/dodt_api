from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_user
from app.dependencies.db_connection import get_db_connection
import asyncpg

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/profile")
async def user_profile(request: Request, user: dict = Depends(get_current_user), conn: asyncpg.Connection = Depends(get_db_connection)):
    # Fetch analysis history
    history = await conn.fetch("""
        SELECT * FROM analysis_results 
        WHERE user_id = $1 
        ORDER BY created_at DESC
    """, int(user["sub"]))
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "history": history
    })
