from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.services.video_service import VideoService
from app.dependencies.auth import get_current_admin
from app.dependencies.db_connection import get_db_connection
import asyncpg
from typing import List

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.post("/upload")
async def upload_video(
    title: str = Form(...),
    video: UploadFile = File(...),
    user: dict = Depends(get_current_admin),
    video_service: VideoService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await video_service.upload_video(conn, title, video, user)

@router.get("/", response_model=List[dict])
async def get_all_videos(
    user: dict = Depends(get_current_admin),
    video_service: VideoService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    videos = await video_service.get_all_videos(conn)
    return [dict(video) for video in videos]

@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    user: dict = Depends(get_current_admin),
    video_service: VideoService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await video_service.delete_video(conn, video_id)
