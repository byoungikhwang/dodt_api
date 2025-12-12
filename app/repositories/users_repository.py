from app.dependencies.db_connection import get_db_connection
from fastapi import Depends
import asyncpg

class UserRepository:
    def __init__(self, db_pool=Depends(get_db_connection)):
        # In this simple setup, db_pool is actually a connection yielded by the dependency
        # But for better pattern, we might want to pass the connection directly to methods
        pass

    async def get_user_by_email(self, conn: asyncpg.Connection, email: str):
        query = "SELECT * FROM users WHERE email = $1"
        return await conn.fetchrow(query, email)

    async def create_user(self, conn: asyncpg.Connection, email: str, name: str, picture: str, role: str = "MEMBER"):
        query = """
            INSERT INTO users (email, name, picture, role)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        return await conn.fetchrow(query, email, name, picture, role)
