import os
import uuid
from fastapi import Depends, UploadFile, HTTPException, status
from app.repositories.video_repository import VideoRepository
import asyncpg
from app.config.settings import settings

class VideoService:
    def __init__(self, video_repo: VideoRepository = Depends()):
        self.video_repo = video_repo
        self.upload_dir = settings.UPLOAD_DIRECTORY
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_video(self, conn: asyncpg.Connection, title: str, video: UploadFile, user: dict):
        # Generate a unique filename to prevent overwrites
        extension = video.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(self.upload_dir, unique_filename)

        # Save the file to disk
        try:
            with open(filepath, "wb") as buffer:
                buffer.write(await video.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save video file: {e}")

        # Create a record in the database
        db_record = await self.video_repo.create_video_record(
            conn=conn,
            title=title,
            filename=video.filename,
            filepath=filepath,
            uploaded_by=int(user["sub"])
        )
        return db_record

    async def get_all_videos(self, conn: asyncpg.Connection):
        return await self.video_repo.get_all_videos(conn)

    async def delete_video(self, conn: asyncpg.Connection, video_id: int):
        # Get video record to find the file path
        video_record = await self.video_repo.get_video_by_id(conn, video_id)
        if not video_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

        # Delete the file from disk
        if os.path.exists(video_record["filepath"]):
            os.remove(video_record["filepath"])
        
        # Delete the record from the database
        deleted_record = await self.video_repo.delete_video_record(conn, video_id)
        return deleted_record
