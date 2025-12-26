# [수정 전] app/routers/auth_router.py
# from fastapi import APIRouter, Depends, Request, HTTPException
# from fastapi.responses import RedirectResponse, JSONResponse
# from fastapi.templating import Jinja2Templates # Import Jinja2Templates

# from app.dependencies.db_connection import get_db_connection
# from app.services.users_service import UserService
# from app.auth.jwt_handler import create_access_token
# from app.config.settings import settings
# import asyncpg
# import secrets
# import httpx

# router = APIRouter()

# # Initialize Jinja2Templates
# templates = Jinja2Templates(directory="app/templates")

# GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
# GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

# @router.get("/login")
# async def login(request: Request):
#     """Serves the login page."""
#     return templates.TemplateResponse("login.html", {"request": request})

# @router.get("/auth/callback")
# async def google_callback(request: Request, code: str, state: str, user_service: UserService = Depends(), conn: asyncpg.Connection = Depends(get_db_connection)):
#     # Verify state to prevent CSRF
#     if state != request.session.pop("state", None):
#         raise HTTPException(status_code=403, detail="Invalid state token")
    
#     token_url = "https://oauth2.googleapis.com/token"
#     data = {
#         "code": code,
#         "client_id": GOOGLE_CLIENT_ID,
#         "client_secret": GOOGLE_CLIENT_SECRET,
#         "redirect_uri": GOOGLE_REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(token_url, data=data)
#         if response.status_code != 200:
#             raise HTTPException(status_code=400, detail="Failed to get token from Google")
        
#         token_data = response.json()
#         access_token = token_data.get("access_token")
        
#         user_info_response = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
#         user_info = user_info_response.json()
        
#         email = user_info.get("email")
#         name = user_info.get("name")
#         picture = user_info.get("picture")
        
#         user = await user_service.get_or_create_user(conn, email, name, picture)
        
#         # Create JWT
#         jwt_token = create_access_token({
#             "sub": str(user["id"]),
#             "email": user["email"],
#             "role": user["role"],
#             "name": user["name"],
#             "picture": user["picture"]
#         })
        
#         # Redirect to dashboard with token (in a real app, maybe set cookie or redirect to a frontend that handles the token)
#         # Or better, set it as a cookie.
#         response = RedirectResponse(url="/dashboard")
#         response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
#         return response

# @router.get("/login/google")
# async def login_google(request: Request):
#     # Generate and store state for CSRF protection
#     state = secrets.token_urlsafe(32)
#     request.session["state"] = state
#     return RedirectResponse(
#         f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20email%20profile&access_type=offline&state={state}"
#     )

# @router.get("/logout")
# async def logout(request: Request):
#     """Logs the user out by clearing the access_token cookie."""
#     response = RedirectResponse(url="/")
#     response.delete_cookie(key="access_token")
#     return response

# [수정 후] app/routers/auth_router.py
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.users_service import UserService
from app.dependencies.services import get_user_service # [수정] 새로운 서비스 의존성 import
from app.auth.jwt_handler import create_access_token
from app.config.settings import settings
import secrets
import httpx

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

@router.get("/login")
async def login(request: Request):
    """Serves the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/auth/callback")
# [수정 전] async def google_callback(request: Request, code: str, state: str, user_service: UserService = Depends(), conn: asyncpg.Connection = Depends(get_db_connection)):
# [수정 후] 올바른 서비스 의존성 주입 사용, conn 제거
async def google_callback(
    request: Request, 
    code: str, 
    state: str, 
    user_service: UserService = Depends(get_user_service)
):
    if state != request.session.pop("state", None):
        raise HTTPException(status_code=403, detail="Invalid state token")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get token from Google")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_response.json()
        
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        
        # [수정 전] user = await user_service.get_or_create_user(conn, email, name, picture)
        # [수정 후] conn 없이 서비스 메소드 호출
        user = await user_service.get_or_create_user(email, name, picture)
        
        jwt_token = create_access_token(data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
            "picture": user["picture"]
        })
        
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
        return response

@router.get("/login/google")
async def login_google(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["state"] = state
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&state={state}"
    )
    return RedirectResponse(google_auth_url)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    return response
