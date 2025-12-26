from fastapi import Depends
import asyncpg
# 1. 기존에 작성하신 db_connection 파일에서 get_db_connection을 가져옵니다.
from app.dependencies.db_connection import get_db_connection
# 2. 각 레포지토리를 가져옵니다.
from app.repositories.users_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository

# 라우터에서 사용할 의존성 함수들입니다.

async def get_user_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> UserRepository:
    """
    get_db_connection을 통해 DB 연결을 얻고,
    그 연결을 UserRepository에 넣어서 반환합니다.
    """
    return UserRepository(conn)

async def get_analysis_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> AnalysisRepository:
    """
    get_db_connection을 통해 DB 연결을 얻고,
    그 연결을 AnalysisRepository에 넣어서 반환합니다.
    """
    return AnalysisRepository(conn)
