# [수정 전] app/services/users_service.py
# import logging
# import random
# import string
# from datetime import date, datetime, timedelta

# from app.repositories.users_repository import UserRepository
# from fastapi import Depends, HTTPException, status
# import asyncpg

# logger = logging.getLogger(__name__)


# class UserService:
#     def __init__(self, user_repo: UserRepository = Depends()):
#         self.user_repo = user_repo

#     def _generate_custom_id(self) -> str:
#         """Generates a unique custom ID in ABC1234 format."""
#         letters = ''.join(random.choices(string.ascii_uppercase, k=3))
#         numbers = ''.join(random.choices(string.digits, k=4))
#         custom_id = f"{letters}{numbers}"
#         return custom_id

#     async def _check_and_grant_daily_credit(self, conn: asyncpg.Connection, user_id: int, current_credits: int, last_grant_date: date) -> int:
#         """
#         Checks if a new day has passed since the last credit grant.
#         If so, grants a new credit (up to a max of 1 free daily credit) and updates the last grant date.
#         Returns the updated credit count.
#         """
#         today = date.today()
#         if last_grant_date < today:
#             # Grant 1 free credit for today
#             updated_credits = current_credits + 1
#             await self.user_repo.update_user_credits(conn, user_id, updated_credits, today)
#             return updated_credits
#         return current_credits

#     async def deduct_credit(self, conn: asyncpg.Connection, user_id: int):
#         """
#         Deducts one credit from the user's balance.
#         Raises HTTPException if user has no credits.
#         """
#         user = await self.user_repo.get_user_by_id(conn, user_id)
#         if not user or user["credits"] <= 0:
#             raise HTTPException(
#                 status_code=status.HTTP_402_PAYMENT_REQUIRED,
#                 detail="Not enough credits. Please try again tomorrow or purchase more."
#             )
        
#         updated_credits = user["credits"] - 1
#         await self.user_repo.update_user_credits(conn, user_id, updated_credits)
#         return updated_credits


#     async def get_or_create_user(self, conn: asyncpg.Connection, email: str, name: str, picture: str):
#         try:
#             # First, attempt to create the user. This is the "optimistic" or "ask for forgiveness" approach.
#             custom_id_exists = True
#             generated_custom_id = ""
#             while custom_id_exists:
#                 generated_custom_id = self._generate_custom_id()
#                 # Check if custom_id already exists
#                 existing_user_with_id = await self.user_repo.get_user_by_custom_id(conn, generated_custom_id)
#                 if not existing_user_with_id:
#                     custom_id_exists = False

#             initial_credits = 1
#             today = date.today()
#             user = await self.user_repo.create_user(
#                 conn, email, generated_custom_id, name, picture, role="MEMBER",
#                 credits=initial_credits, last_credit_grant_date=today
#             )
#             # If creation is successful, the new user is returned.
#             return user
#         except asyncpg.UniqueViolationError:
#             # If a UniqueViolationError occurs, it means the user was likely created by a concurrent request.
#             logger.info(f"Race condition handled: User with email {email} already exists. Fetching existing user.")
            
#             # The transaction is automatically rolled back by asyncpg driver in case of such error.
#             # We can now safely fetch the existing user in a new transaction context provided by Depends.
#             user = await self.user_repo.get_user_by_email(conn, email)
#             if not user:
#                 # This case is highly unlikely but handled for safety.
#                 raise HTTPException(status_code=500, detail="Failed to retrieve user after race condition.")

#             # Proceed with the daily credit check for the existing user.
#             last_grant_date = user["last_credit_grant_date"]
#             if not isinstance(last_grant_date, date):
#                 # If it's None or some other unexpected type, treat as a grant-requiring date.
#                 last_grant_date = date(1970, 1, 1)

#             await self._check_and_grant_daily_credit(conn, user["id"], user["credits"], last_grant_date)
            
#             # Re-fetch the user to get the most up-to-date credit information.
#             user = await self.user_repo.get_user_by_id(conn, user["id"])
#             return user

#     async def update_user_by_admin(self, conn: asyncpg.Connection, user_id: int, name: str, role: str, credits: int):
#         """
#         Updates user information (name, role, credits) by an admin.
#         """
#         updated_user = await self.user_repo.update_user(conn, user_id, name, role, credits)
#         return updated_user

#     async def delete_user_by_admin(self, conn: asyncpg.Connection, user_id: int) -> bool:
#         """
#         Deletes a user by their ID by an admin.
#         """
#         deleted_count = await self.user_repo.delete_user(conn, user_id)
#         return deleted_count > 0

# [수정 후] app/services/users_service.py
import logging
import random
import string
from datetime import date
from typing import Optional, List

from app.repositories.users_repository import UserRepository
from fastapi import HTTPException, status
import asyncpg

logger = logging.getLogger(__name__)


class UserService:
    # [수정 전] __init__에서 Depends 사용
    # def __init__(self, user_repo: UserRepository = Depends()):
    # [수정 후] 순수 Python __init__으로 변경. 의존성은 라우터에서 주입받음
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _generate_custom_id(self) -> str:
        """Generates a unique custom ID in ABC1234 format."""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=4))
        custom_id = f"{letters}{numbers}"
        return custom_id

    async def _check_and_grant_daily_credit(self, user_id: int, current_credits: int, last_grant_date: date) -> int:
        """
        Checks if a new day has passed since the last credit grant.
        If so, grants a new credit (up to a max of 1 free daily credit) and updates the last grant date.
        Returns the updated credit count.
        """
        today = date.today()
        if last_grant_date < today:
            updated_credits = current_credits + 1
            # [수정 전] conn 전달
            # await self.user_repo.update_user_credits(conn, user_id, updated_credits, today)
            # [수정 후] conn 제거
            await self.user_repo.update_user_credits(user_id, updated_credits, today)
            return updated_credits
        return current_credits

    async def deduct_credit(self, user_id: int):
        """
        Deducts one credit from the user's balance.
        Raises HTTPException if user has no credits.
        """
        # [수정 전] conn 전달
        # user = await self.user_repo.get_user_by_id(conn, user_id)
        # [수정 후] conn 제거
        user = await self.user_repo.get_user_by_id(user_id)
        if not user or user["credits"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Not enough credits. Please try again tomorrow or purchase more."
            )
        
        updated_credits = user["credits"] - 1
        # [수정 전] conn 전달
        # await self.user_repo.update_user_credits(conn, user_id, updated_credits)
        # [수정 후] conn 제거
        await self.user_repo.update_user_credits(user_id, updated_credits)
        return updated_credits


    async def get_or_create_user(self, email: str, name: Optional[str], picture: Optional[str]) -> asyncpg.Record:
        try:
            custom_id_exists = True
            generated_custom_id = ""
            while custom_id_exists:
                generated_custom_id = self._generate_custom_id()
                # [수정 전] conn 전달
                # existing_user_with_id = await self.user_repo.get_user_by_custom_id(conn, generated_custom_id)
                # [수정 후] conn 제거
                existing_user_with_id = await self.user_repo.get_user_by_custom_id(generated_custom_id)
                if not existing_user_with_id:
                    custom_id_exists = False

            initial_credits = 1
            today = date.today()
            # [수정 전] conn 전달
            # user = await self.user_repo.create_user(
            #     conn, email, generated_custom_id, name, picture, role="MEMBER",
            #     credits=initial_credits, last_credit_grant_date=today
            # )
            # [수정 후] conn 제거
            user = await self.user_repo.create_user(
                email, generated_custom_id, name, picture, role="MEMBER",
                credits=initial_credits, last_credit_grant_date=today
            )
            return user
        except asyncpg.UniqueViolationError:
            logger.info(f"Race condition handled: User with email {email} already exists. Fetching existing user.")
            
            # [수정 전] conn 전달
            # user = await self.user_repo.get_user_by_email(conn, email)
            # [수정 후] conn 제거
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise HTTPException(status_code=500, detail="Failed to retrieve user after race condition.")

            last_grant_date_val = user["last_credit_grant_date"]
            if not isinstance(last_grant_date_val, date):
                last_grant_date_val = date(1970, 1, 1)

            await self._check_and_grant_daily_credit(user["id"], user["credits"], last_grant_date_val)
            
            # [수정 전] conn 전달
            # user = await self.user_repo.get_user_by_id(conn, user["id"])
            # [수정 후] conn 제거
            user = await self.user_repo.get_user_by_id(user["id"])
            return user

    async def update_user_by_admin(self, user_id: int, name: str, role: str, credits: int) -> Optional[asyncpg.Record]:
        """
        Updates user information (name, role, credits) by an admin.
        """
        # [수정 전] conn 전달
        # updated_user = await self.user_repo.update_user(conn, user_id, name, role, credits)
        # [수정 후] conn 제거
        updated_user = await self.user_repo.update_user(user_id, name, role, credits)
        return updated_user

    async def delete_user_by_admin(self, user_id: int) -> bool:
        """
        Deletes a user by their ID by an admin.
        """
        # [수정 전] conn 전달
        # deleted_count = await self.user_repo.delete_user(conn, user_id)
        # [수정 후] conn 제거
        deleted_count = await self.user_repo.delete_user(user_id)
        return deleted_count > 0

    async def get_users_count(self) -> int:
        """ [신규] 전체 사용자 수를 조회합니다. """
        return await self.user_repo.get_users_count()

    async def get_all_users(self, offset: int = 0, limit: int = 50) -> List[asyncpg.Record]:
        """ [신규] 모든 사용자를 페이지네이션하여 조회합니다. """
        return await self.user_repo.get_all_users(offset=offset, limit=limit)
