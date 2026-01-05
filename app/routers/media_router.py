from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from app.services.media_service import MediaService
from app.dependencies.auth import get_current_admin, get_current_user, get_optional_user
from app.dependencies.db_connection import get_db_connection
import asyncpg
import asyncio
from typing import List, Optional
from app.schemas import MediaListResponse

router = APIRouter(prefix="/api/media", tags=["media"])

@router.post("/upload")
async def upload_media(
    title: str = Form(...),
    description: str = Form(...),
    media_type: str = Form(...),
    hashtags: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_admin), # Admin-only upload
    media_service: MediaService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await media_service.upload_media(conn, title, description, media_type, hashtags, file, user)

@router.get("/", response_model=MediaListResponse)
async def get_feed_media(
    sort: str = Query('latest', enum=['latest', 'popular']),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: Optional[dict] = Depends(get_optional_user),
    media_service: MediaService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    try:
        offset = (page - 1) * limit
        current_user_id = int(user["sub"]) if user else None

        # Fetch media items and total count concurrently
        results = await asyncio.gather(
            media_service.get_feed_media(conn, sort, search, limit, offset, current_user_id=current_user_id),
            media_service.get_total_media_count(conn, search)
        )
        media_items, total = results[0], results[1]

        total_pages = (total + limit - 1) // limit

        return {
            "success": True,
            "data": media_items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        # Proper logging should be implemented here
        print(f"Error fetching feed media: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the feed.")

@router.post("/{media_id}/like", status_code=200)
async def toggle_media_like(
    media_id: int,
    user: dict = Depends(get_current_user),
    media_service: MediaService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    user_id = int(user["sub"])
    return await media_service.toggle_like(conn, media_id, user_id)

@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    user: dict = Depends(get_current_admin), # Admin-only delete
    media_service: MediaService = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    return await media_service.delete_media(conn, media_id)