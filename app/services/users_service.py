from app.repositories.users_repository import UserRepository
from fastapi import Depends
import asyncpg

class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    async def get_or_create_user(self, conn: asyncpg.Connection, email: str, name: str, picture: str):
        user = await self.user_repo.get_user_by_email(conn, email)
        if not user:
            user = await self.user_repo.create_user(conn, email, name, picture, role="MEMBER")
        return user
