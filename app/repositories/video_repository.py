from app.dependencies.db_connection import get_db_connection
from fastapi import Depends
import asyncpg
from datetime import date

class VideoRepository:
    async def create_video_record(self, conn: asyncpg.Connection, title: str, filename: str, filepath: str, uploaded_by: int):
        query = """
            INSERT INTO videos (title, filename, filepath, uploaded_by)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        return await conn.fetchrow(query, title, filename, filepath, uploaded_by)

    async def get_all_videos(self, conn: asyncpg.Connection):
        query = "SELECT * FROM videos ORDER BY created_at DESC"
        return await conn.fetch(query)

    async def get_video_by_id(self, conn: asyncpg.Connection, video_id: int):
        query = "SELECT * FROM videos WHERE id = $1"
        return await conn.fetchrow(query, video_id)

    async def delete_video_record(self, conn: asyncpg.Connection, video_id: int):
        query = "DELETE FROM videos WHERE id = $1 RETURNING *"
        return await conn.fetchrow(query, video_id)
