from app.dependencies.db_connection import get_db_connection
from fastapi import Depends
import asyncpg
from datetime import date # Import date for type hinting

class UserRepository:

    async def get_user_by_email(self, conn: asyncpg.Connection, email: str):
        query = "SELECT * FROM users WHERE email = $1"
        return await conn.fetchrow(query, email)

    async def get_user_by_id(self, conn: asyncpg.Connection, user_id: int):
        query = "SELECT * FROM users WHERE id = $1"
        return await conn.fetchrow(query, user_id)

    async def get_user_by_custom_id(self, conn: asyncpg.Connection, custom_id: str):
        query = "SELECT * FROM users WHERE custom_id = $1"
        return await conn.fetchrow(query, custom_id)

    async def create_user(self, conn: asyncpg.Connection, email: str, custom_id: str, name: str, picture: str, role: str = "MEMBER", credits: int = 1, last_credit_grant_date: date = None):
        query = """
            INSERT INTO users (email, custom_id, name, picture, role, credits, last_credit_grant_date)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await conn.fetchrow(query, email, custom_id, name, picture, role, credits, last_credit_grant_date)

    async def update_user_credits(self, conn: asyncpg.Connection, user_id: int, new_credits: int, last_credit_grant_date: date = None):
        if last_credit_grant_date:
            query = "UPDATE users SET credits = $1, last_credit_grant_date = $2 WHERE id = $3 RETURNING *"
            return await conn.fetchrow(query, new_credits, last_credit_grant_date, user_id)
        else:
            query = "UPDATE users SET credits = $1 WHERE id = $2 RETURNING *"
            return await conn.fetchrow(query, new_credits, user_id)

    async def update_user(self, conn: asyncpg.Connection, user_id: int, name: str, role: str, credits: int):
        query = """
            UPDATE users SET name = $1, role = $2, credits = $3 WHERE id = $4 RETURNING *
        """
        return await conn.fetchrow(query, name, role, credits, user_id)

    async def delete_user(self, conn: asyncpg.Connection, user_id: int) -> int:
        query = "DELETE FROM users WHERE id = $1"
        status = await conn.execute(query, user_id)
        return int(status.split()[-1]) # Return the number of deleted rows

    async def get_user_email_by_id(self, conn: asyncpg.Connection, user_id: int) -> str | None:
        query = "SELECT email FROM users WHERE id = $1"
        record = await conn.fetchrow(query, user_id)
        return record["email"] if record else None