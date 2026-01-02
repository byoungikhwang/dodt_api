# app/repositories/user_repository.py

import asyncpg
from datetime import date
from typing import Optional, List

class UserRepository:
    def __init__(self, conn: asyncpg.Connection):
        """
        초기화 시점에 DB 연결 객체를 주입받습니다.
        """
        self.conn = conn

    async def get_user_by_email(self, email: str) -> Optional[asyncpg.Record]:
        query = "SELECT * FROM users WHERE email = $1"
        return await self.conn.fetchrow(query, email)

    async def get_user_by_id(self, user_id: int) -> Optional[asyncpg.Record]:
        query = "SELECT * FROM users WHERE id = $1"
        return await self.conn.fetchrow(query, user_id)

    async def get_user_by_id_for_update(self, user_id: int) -> Optional[asyncpg.Record]:
        query = "SELECT * FROM users WHERE id = $1 FOR UPDATE"
        return await self.conn.fetchrow(query, user_id)

    async def get_user_by_custom_id(self, custom_id: str) -> Optional[asyncpg.Record]:
        query = "SELECT * FROM users WHERE custom_id = $1"
        return await self.conn.fetchrow(query, custom_id)

    async def create_user(
        self, 
        email: str, 
        custom_id: str, 
        name: str, 
        picture: str, 
        role: str = "MEMBER", 
        credits: int = 1, 
        last_credit_grant_date: Optional[date] = None
    ) -> asyncpg.Record:
        query = """
            INSERT INTO users (email, custom_id, name, picture, role, credits, last_credit_grant_date)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await self.conn.fetchrow(query, email, custom_id, name, picture, role, credits, last_credit_grant_date)

    async def update_user_credits(self, user_id: int, new_credits: int, last_credit_grant_date: Optional[date] = None) -> Optional[asyncpg.Record]:
        if last_credit_grant_date:
            query = "UPDATE users SET credits = $1, last_credit_grant_date = $2 WHERE id = $3 RETURNING *"
            return await self.conn.fetchrow(query, new_credits, last_credit_grant_date, user_id)
        else:
            query = "UPDATE users SET credits = $1 WHERE id = $2 RETURNING *"
            return await self.conn.fetchrow(query, new_credits, user_id)

    async def update_user(self, user_id: int, name: str, role: str, credits: int) -> Optional[asyncpg.Record]:
        query = """
            UPDATE users SET name = $1, role = $2, credits = $3 WHERE id = $4 RETURNING *
        """
        return await self.conn.fetchrow(query, name, role, credits, user_id)

    async def delete_user(self, user_id: int) -> int:
        query = "DELETE FROM users WHERE id = $1"
        status = await self.conn.execute(query, user_id)
        # Safely parse the status string like 'DELETE 1'
        try:
            return int(status.split()[-1])
        except (ValueError, IndexError):
            return 0

    async def get_user_email_by_id(self, user_id: int) -> Optional[str]:
        # fetchval을 사용하여 단일 값만 깔끔하게 가져옵니다.
        query = "SELECT email FROM users WHERE id = $1"
        return await self.conn.fetchval(query, user_id)

    async def get_users_count(self) -> int:
        """ [신규] 전체 사용자 수를 조회합니다. """
        query = "SELECT COUNT(*) FROM users"
        return await self.conn.fetchval(query)

    async def get_all_users(self, offset: int = 0, limit: int = 50) -> List[asyncpg.Record]:
        """ [신규] 모든 사용자를 페이지네이션하여 조회합니다. """
        query = "SELECT * FROM users ORDER BY id DESC LIMIT $1 OFFSET $2"
        return await self.conn.fetch(query, limit, offset)