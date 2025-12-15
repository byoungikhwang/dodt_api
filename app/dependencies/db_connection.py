from fastapi import Request
import asyncpg

async def get_db_connection(request: Request):
    """
    Yields a database connection from the application's connection pool.
    The connection is automatically released back to the pool when the request is finished.
    """
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        yield connection
