import asyncpg
from typing import List

class StyleLogRepository:
    def __init__(self, conn: asyncpg.Connection):
        """
        초기화 시점에 DB 연결 객체를 주입받습니다.
        """
        self.conn = conn

    async def get_all_style_logs(self) -> List[asyncpg.Record]:
        """
        모든 스타일 로그를 시간 역순으로 조회합니다.
        """
        query = "SELECT * FROM style_logs ORDER BY created_at DESC"
        return await self.conn.fetch(query)
