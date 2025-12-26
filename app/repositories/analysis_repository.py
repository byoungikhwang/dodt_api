import asyncpg
from typing import List

class AnalysisRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_history_by_user_id(self, user_id: int) -> List[asyncpg.Record]:
        query = """
            SELECT * FROM analysis_results 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """
        return await self.conn.fetch(query, user_id)