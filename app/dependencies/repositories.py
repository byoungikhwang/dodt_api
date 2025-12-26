from fastapi import Depends
import asyncpg
from app.dependencies.db_connection import get_db_connection
# 방금 만든 AnalysisRepository를 가져옵니다.
from app.repositories.analysis_repository import AnalysisRepository
# (만약 UserRepository도 있다면 여기에 함께 import 되어 있을 것입니다)

async def get_analysis_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> AnalysisRepository:
    """
    DB 연결을 획득하고, 이를 포함한 AnalysisRepository 인스턴스를 반환합니다.
    """
    return AnalysisRepository(conn)