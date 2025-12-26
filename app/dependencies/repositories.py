from fastapi import Depends
import asyncpg
from app.dependencies.db_connection import get_db_connection
from app.repositories.users_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.style_log_repository import StyleLogRepository

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
    DB 연결을 획득하고, 이를 포함한 AnalysisRepository 인스턴스를 반환합니다.
    """
    return AnalysisRepository(conn)

async def get_style_log_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> StyleLogRepository:
    """
    DB 연결을 획득하고, 이를 포함한 StyleLogRepository 인스턴스를 반환합니다.
    """
    return StyleLogRepository(conn)
