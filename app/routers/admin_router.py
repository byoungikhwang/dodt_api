from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin, get_current_admin_or_redirect
from app.dependencies.db_connection import get_db_connection
from app.services.users_service import UserService # Import UserService
from app.services.analysis_service import AnalysisService # Import AnalysisService
import asyncpg
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

class UserUpdate(BaseModel):
    name: str
    role: str
    credits: int

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
async def get_all_users(admin_user: dict = Depends(get_current_admin_or_redirect), conn: asyncpg.Connection = Depends(get_db_connection)):
    """
    Returns a list of all users. Accessible only by admins.
    """
    users = await conn.fetch("SELECT id, email, name, custom_id, role, credits, created_at FROM users ORDER BY id ASC")
    return [dict(user) for user in users]

@router.put("/users/{user_id}")
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    admin_user: dict = Depends(get_current_admin), 
    user_service: UserService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    try:
        updated_user = await user_service.update_user_by_admin(conn, user_id, user_update.name, user_update.role, user_update.credits)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated successfully", "user": updated_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, 
    admin_user: dict = Depends(get_current_admin),
    user_service: UserService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    try:
        deleted = await user_service.delete_user_by_admin(conn, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis-history")
async def get_all_analysis_history(
    admin_user: dict = Depends(get_current_admin_or_redirect),
    analysis_service: AnalysisService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Returns all analysis results. Accessible only by admins.
    """
    history = await analysis_service.get_all_analysis_results(conn)
    return history

@router.get("/style-logs")
async def get_all_style_logs(
    admin_user: dict = Depends(get_current_admin_or_redirect),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Returns all style logs. Accessible only by admins.
    """
    # Assuming a direct fetch for style logs for now, or a dedicated service method will be created
    logs = await conn.fetch("SELECT * FROM style_logs ORDER BY created_at DESC")
    return [dict(log) for log in logs]


@router.get("/videos")
async def video_management_page(request: Request, user: dict = Depends(get_current_admin_or_redirect)):
    """Serves the video management page for admins."""
    return templates.TemplateResponse("admin_videos.html", {"request": request, "user": user})
