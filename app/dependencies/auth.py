from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse # Import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import verify_token
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_optional_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        # Try to get from cookie
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            # Remove "Bearer " prefix if present
            if cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            else:
                token = cookie_token
    
    if not token:
        return None

    payload = verify_token(token)
    return payload

async def get_current_user(user: Optional[dict] = Depends(get_optional_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_user_or_redirect(user: Optional[dict] = Depends(get_optional_user)):
    """
    Dependency that requires a user to be authenticated.
    If the user is not authenticated, it redirects to the /login page.
    """
    if not user:
        return RedirectResponse(url="/login")
    return user

async def get_current_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return user

async def get_current_admin_or_redirect(user: dict = Depends(get_current_user_or_redirect)):
    """
    Dependency that requires a user to be an admin.
    If the user is not authenticated, redirects to /login.
    If the user is not an admin, raises a 403 Forbidden error.
    """
    # get_current_user_or_redirect will return a RedirectResponse if not logged in
    # which FastAPI will handle, so we only need to check the role.
    if user and user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this page.",
        )
    return user
