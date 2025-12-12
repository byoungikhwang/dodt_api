from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.middlewares.logging_middleware import LoggingMiddleware
# [Modified] recommend_router 추가 임포트
from app.routers import auth_router, index_router, analysis_router, admin_router, user_router, recommend_router

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

@app.on_event("startup")
async def startup_event():
    print("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown")
