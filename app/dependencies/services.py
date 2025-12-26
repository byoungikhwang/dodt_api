from fastapi import Depends
from app.services.users_service import UserService
from app.services.analysis_service import AnalysisService
from app.repositories.users_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.style_log_repository import StyleLogRepository
from app.dependencies.repositories import (
    get_user_repository, 
    get_analysis_repository,
    get_style_log_repository
)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """
    UserRepository에 의존하는 UserService를 생성하고 반환합니다.
    """
    return UserService(user_repo)

def get_analysis_service(
    user_repo: UserRepository = Depends(get_user_repository),
    analysis_repo: AnalysisRepository = Depends(get_analysis_repository),
    style_log_repo: StyleLogRepository = Depends(get_style_log_repository)
) -> AnalysisService:
    """
    필요한 모든 Repository에 의존하는 AnalysisService를 생성하고 반환합니다.
    """
    return AnalysisService(
        user_repo=user_repo,
        analysis_repo=analysis_repo,
        style_log_repo=style_log_repo
    )
