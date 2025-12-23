import os
import uuid
import re
from fastapi import Depends, UploadFile, HTTPException, status
from app.repositories.media_repository import MediaRepository
import asyncpg
from app.config.settings import settings
from typing import List, Optional

class MediaService:
    def __init__(self, media_repo: MediaRepository = Depends()):
        self.media_repo = media_repo
        self.upload_dir = settings.UPLOAD_DIRECTORY
        os.makedirs(self.upload_dir, exist_ok=True)

    def _parse_hashtags(self, s: str) -> List[str]:
        # Find all hashtags starting with # and followed by non-space characters
        return re.findall(r"(#\w+)", s)

    async def upload_media(self, conn: asyncpg.Connection, title: str, description: str, media_type: str, hashtags_str: str, file: UploadFile, user: dict):
        extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        url = f"/static/uploads/{unique_filename}"
        file_path_on_disk = os.path.join(self.upload_dir, unique_filename)

        try:
            with open(file_path_on_disk, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save media file: {e}")

        hashtags = self._parse_hashtags(hashtags_str)

        db_record = await self.media_repo.create_media_record(
            conn=conn,
            user_id=int(user["sub"]),
            title=title,
            description=description,
            media_type=media_type,
            url=url,
            hashtags=hashtags
        )
        return db_record

    async def get_feed_media(self, conn: asyncpg.Connection, sort: str, search: Optional[str], limit: int, offset: int, current_user_id: Optional[int]):
        media_items = await self.media_repo.get_feed_media(conn, sort, search, limit, offset, current_user_id)
        return [dict(item) for item in media_items]

    async def toggle_like(self, conn: asyncpg.Connection, media_id: int, user_id: int):
        # Check if media exists
        media = await self.media_repo.get_media_by_id(conn, media_id)
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

        like = await self.media_repo.find_like(conn, user_id, media_id)
        if like:
            await self.media_repo.remove_like(conn, user_id, media_id)
            return {"status": "unliked"}
        else:
            await self.media_repo.add_like(conn, user_id, media_id)
            return {"status": "liked"}

    async def delete_media(self, conn: asyncpg.Connection, media_id: int):
        media_record = await self.media_repo.get_media_by_id(conn, media_id)
        if not media_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

        file_path_on_disk = os.path.join(settings.UPLOAD_DIRECTORY, os.path.basename(media_record["url"]))
        if os.path.exists(file_path_on_disk):
            os.remove(file_path_on_disk)
        
        deleted_record = await self.media_repo.delete_media_record(conn, media_id)
        return deleted_record