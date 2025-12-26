import asyncpg
import json
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
        [이름 수정] 특정 사용자의 모든 분석 결과 이력을 시간 역순으로 조회합니다.
        """
        query = """
            SELECT id, user_id, result_data, created_at 
            FROM analysis_results 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """
        records = await self.conn.fetch(query, user_id)
        return [AnalysisResult.model_validate(record) for record in records]

    async def create_analysis_result(
        self, user_id: int, filename: str, filelink: str, result: dict
    ) -> asyncpg.Record:
        """
        [신규] 분석 결과를 데이터베이스에 저장합니다.
        """
        query = """
            INSERT INTO analysis_results (user_id, filename, filelink, result)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        # The result dictionary is converted to a JSON string for storage.
        return await self.conn.fetchrow(query, user_id, filename, filelink, json.dumps(result))

    async def get_all_analysis_results(self) -> List[asyncpg.Record]:
        """
        [신규] 모든 분석 결과를 시간 역순으로 조회합니다.
        """
        query = "SELECT * FROM analysis_results ORDER BY created_at DESC"
        return await self.conn.fetch(query)