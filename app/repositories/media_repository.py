import asyncpg
from typing import List, Optional

class MediaRepository:
    async def create_media_record(self, conn: asyncpg.Connection, user_id: int, title: str, description: str, media_type: str, url: str, hashtags: List[str]):
        query = """
            INSERT INTO media (user_id, title, description, media_type, url, hashtags)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        return await conn.fetchrow(query, user_id, title, description, media_type, url, hashtags)

    async def get_feed_media(self, conn: asyncpg.Connection, sort: str, search: Optional[str], limit: int, offset: int, current_user_id: Optional[int] = None):
        params = []
        param_idx = 1

        liked_by_user_expression = "COALESCE(bool_or(ml.user_id = $1), FALSE) as liked_by_user"
        if current_user_id:
            params.append(current_user_id)
            param_idx += 1
        else:
            liked_by_user_expression = "FALSE as liked_by_user"

        query = f"""
            SELECT
                m.id, m.user_id, m.title, m.description, m.media_type, m.url, m.hashtags, m.created_at,
                u.name as creator_name,
                u.picture as creator_picture,
                COUNT(ml.media_id) as like_count,
                {liked_by_user_expression}
            FROM media m
            JOIN users u ON m.user_id = u.id
            LEFT JOIN media_likes ml ON m.id = ml.media_id
        """

        where_clauses = []
        if search:
            if search.startswith('#'):
                where_clauses.append(f"EXISTS (SELECT 1 FROM unnest(m.hashtags) AS hashtag WHERE lower(hashtag) = lower(${param_idx}))")
                params.append(search)
                param_idx += 1
            else:
                where_clauses.append(f"(m.title ILIKE ${param_idx} OR m.description ILIKE ${param_idx})")
                params.append(f"%{search}%")
                param_idx += 1
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " GROUP BY m.id, m.user_id, m.title, m.description, m.media_type, m.url, m.hashtags, m.created_at, u.name, u.picture"

        if sort == 'popular':
            query += " ORDER BY like_count DESC, m.created_at DESC"
        else: # Default to 'latest'
            query += " ORDER BY m.created_at DESC"

        query += f" LIMIT ${param_idx} OFFSET ${param_idx + 1}"
        params.extend([limit, offset])

        return await conn.fetch(query, *params)

    async def get_total_media_count(self, conn: asyncpg.Connection, search: Optional[str]):
        params = []
        param_idx = 1
        
        query = "SELECT COUNT(DISTINCT m.id) FROM media m"
        
        where_clauses = []
        if search:
            if search.startswith('#'):
                where_clauses.append(f"EXISTS (SELECT 1 FROM unnest(m.hashtags) AS hashtag WHERE lower(hashtag) = lower(${param_idx}))")
                params.append(search)
                param_idx += 1
            else:
                where_clauses.append(f"(m.title ILIKE ${param_idx} OR m.description ILIKE ${param_idx})")
                params.append(f"%{search}%")
                param_idx += 1

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        count_record = await conn.fetchrow(query, *params)
        return count_record[0] if count_record else 0

    async def get_media_by_id(self, conn: asyncpg.Connection, media_id: int):
        query = "SELECT * FROM media WHERE id = $1"
        return await conn.fetchrow(query, media_id)

    async def delete_media_record(self, conn: asyncpg.Connection, media_id: int):
        query = "DELETE FROM media WHERE id = $1 RETURNING *"
        return await conn.fetchrow(query, media_id)
        
    async def find_like(self, conn: asyncpg.Connection, user_id: int, media_id: int):
        query = "SELECT * FROM media_likes WHERE user_id = $1 AND media_id = $2"
        return await conn.fetchrow(query, user_id, media_id)

    async def add_like(self, conn: asyncpg.Connection, user_id: int, media_id: int):
        query = "INSERT INTO media_likes (user_id, media_id) VALUES ($1, $2) RETURNING *"
        return await conn.fetchrow(query, user_id, media_id)

    async def remove_like(self, conn: asyncpg.Connection, user_id: int, media_id: int):
        query = "DELETE FROM media_likes WHERE user_id = $1 AND media_id = $2 RETURNING *"
        return await conn.fetchrow(query, user_id, media_id)