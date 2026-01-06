from fastapi import Depends
import asyncpg
from app.dependencies.db_connection import get_db_connection
from app.repositories.users_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.style_log_repository import StyleLogRepository
from app.repositories.media_repository import MediaRepository

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


async def get_media_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> MediaRepository:
    """
    MediaRepository 인스턴스를 반환합니다.
    현재 `MediaRepository`는 메서드 수준에서 `conn`을 인자로 받으므로
    인스턴스 생성 시에는 conn을 저장하지 않습니다. 향후 리팩터링 시
    생성자 인자로 conn을 전달하는 방식으로 변경할 수 있습니다.
    """
    return MediaRepository()
