# app/repositories/analysis_repository.py

import asyncpg
from typing import List
from app.schemas import AnalysisResult

class AnalysisRepository:
    def __init__(self, conn: asyncpg.Connection):
        """
        초기화 시점에 DB 연결 객체를 주입받습니다.
        """
        self.conn = conn

    async def get_analysis_history_by_user_id(self, user_id: int) -> List[AnalysisResult]:
        """
        특정 사용자의 모든 분석 결과 이력을 시간 역순으로 조회합니다.
        """
        query = """
            SELECT id, user_id, result_data, created_at 
            FROM analysis_results 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """
        records = await self.conn.fetch(query, user_id)
        # asyncpg.Record 객체를 AnalysisResult Pydantic 모델로 변환하여 반환합니다.
        return [AnalysisResult.model_validate(record) for record in records]
