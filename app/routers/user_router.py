# [수정 전] 직접적인 DB 의존성 및 쿼리
# from app.dependencies.db_connection import get_db_connection
# import asyncpg

# [수정 후] Repository 의존성으로 교체
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.dependencies.auth import get_current_user_or_redirect
from app.dependencies.repositories import get_analysis_repository
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas import AnalysisResult

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/profile", response_model=List[AnalysisResult])
async def user_profile(
    request: Request, 
    user: dict = Depends(get_current_user_or_redirect),
    # [수정 전] conn: asyncpg.Connection = Depends(get_db_connection)
    # [수정 후] Repository를 주입받도록 변경
    analysis_repo: AnalysisRepository = Depends(get_analysis_repository)
):
    if isinstance(user, RedirectResponse):
        return user

    # [수정 전] 라우터 내부에 있던 데이터베이스 쿼리
    # history = await conn.fetch("""
    #     SELECT * FROM analysis_results 
    #     WHERE user_id = $1 
    #     ORDER BY created_at DESC
    # """, int(user["sub"]))

    # [수정 후] Repository의 메서드를 호출하여 데이터 조회
    history = await analysis_repo.get_analysis_history_by_user_id(user_id=int(user["sub"]))
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "history": history
    })
