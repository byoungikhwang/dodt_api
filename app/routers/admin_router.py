from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin, get_current_admin_or_redirect
from app.services.users_service import UserService
from app.services.analysis_service import AnalysisService
from app.dependencies.services import get_user_service, get_analysis_service
from app.schemas import UserUpdate # Import UserUpdate from schemas
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def admin_dashboard(
    request: Request, 
    user: dict = Depends(get_current_admin_or_redirect), 
    user_service: UserService = Depends(get_user_service)
):
    users_count = await user_service.get_users_count()
    members = await user_service.get_all_users(limit=50)
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user,
        "users_count": users_count,
        "members": members
    })

@router.get("/users", response_model=List[dict])
async def get_all_users_api(
    admin_user: dict = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
    offset: int = 0,
    limit: int = Query(default=100, lte=1000)
):
    users = await user_service.get_all_users(offset=offset, limit=limit)
    return [dict(user) for user in users]

@router.put("/users/{user_id}")
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    admin_user: dict = Depends(get_current_admin), 
    user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user_by_admin(
        user_id, user_update.name, user_update.role, user_update.credits
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully", "user": dict(updated_user)}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, 
    admin_user: dict = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
):
    deleted = await user_service.delete_user_by_admin(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found or could not be deleted.")
    return {"message": "User deleted successfully"}

@router.get("/analysis-history")
async def get_all_analysis_history(
    admin_user: dict = Depends(get_current_admin),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    history = await analysis_service.get_all_analysis_results()
    return history

@router.get("/style-logs")
async def get_all_style_logs(
    admin_user: dict = Depends(get_current_admin),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    logs = await analysis_service.get_all_style_logs()
    return logs

@router.get("/videos")
async def video_management_page(request: Request, user: dict = Depends(get_current_admin_or_redirect)):
    """Serves the video management page for admins."""
    return templates.TemplateResponse("admin_videos.html", {"request": request, "user": user})
