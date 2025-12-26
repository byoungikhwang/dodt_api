from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_user_or_redirect
# [수정 1] get_db_connection을 제거하고, 대신 리포지토리 의존성을 가져옵니다.
from app.dependencies.repositories import get_analysis_repository
from app.repositories.analysis_repository import AnalysisRepository

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/profile")
async def user_profile(
    request: Request, 
    user: dict = Depends(get_current_user_or_redirect),
    # [수정 2] conn: asyncpg.Connection 대신 analysis_repo를 주입받습니다.
    analysis_repo: AnalysisRepository = Depends(get_analysis_repository)
):
    if isinstance(user, RedirectResponse):
        return user

    # [수정 3] SQL 쿼리 문자열을 모두 지우고, 메서드 호출로 변경합니다.
    history = await analysis_repo.get_history_by_user_id(int(user["sub"]))
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "history": history
    })
