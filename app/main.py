import logging
import asyncpg
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.middlewares.logging_middleware import LoggingMiddleware
# [Modified] recommend_router 추가 임포트
from app.routers import auth_router, index_router, analysis_router, admin_router, user_router, recommend_router, n8n_router, video_router

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Middleware
app.add_middleware(LoggingMiddleware)

# Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth_router.router)
app.include_router(index_router.router)
app.include_router(analysis_router.router)
app.include_router(admin_router.router)
app.include_router(user_router.router)
# [Added] AI 추천 라우터 등록
app.include_router(recommend_router.router)
# [Added] n8n 연동 라우터 등록
app.include_router(n8n_router.router)
# [Added] Video management 라우터 등록
app.include_router(video_router.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application started. Connecting to database...")
    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=5,
            max_size=20
        )
        logger.info("Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown. Closing database connection pool...")
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()
        logger.info("Database connection pool closed.")