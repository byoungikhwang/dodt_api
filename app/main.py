import logging
import asyncpg
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.middlewares.logging_middleware import LoggingMiddleware
from starlette.middleware.sessions import SessionMiddleware
# [Modified] recommend_router 추가 임포트
from app.routers import auth_router, index_router, analysis_router, admin_router, user_router, recommend_router, n8n_router, media_router # Changed video_router to media_router

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

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
# [Added] Media management 라우터 등록 (Changed from Video management)
app.include_router(media_router.router)

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
        raise e # Re-raise the exception to stop the application startup


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown. Closing database connection pool...")
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()
        logger.info("Database connection pool closed.")