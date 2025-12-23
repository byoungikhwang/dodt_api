import random
import string
from datetime import date, datetime, timedelta

from app.repositories.users_repository import UserRepository
from fastapi import Depends, HTTPException, status
import asyncpg

class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    def _generate_custom_id(self) -> str:
        """Generates a unique custom ID in ABC1234 format."""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=4))
        custom_id = f"{letters}{numbers}"
        return custom_id

    async def _check_and_grant_daily_credit(self, conn: asyncpg.Connection, user_id: int, current_credits: int, last_grant_date: date) -> int:
        """
        Checks if a new day has passed since the last credit grant.
        If so, grants a new credit (up to a max of 1 free daily credit) and updates the last grant date.
        Returns the updated credit count.
        """
        today = date.today()
        if last_grant_date < today:
            # Grant 1 free credit for today
            updated_credits = current_credits + 1
            await self.user_repo.update_user_credits(conn, user_id, updated_credits, today)
            return updated_credits
        return current_credits

    async def deduct_credit(self, conn: asyncpg.Connection, user_id: int):
        """
        Deducts one credit from the user's balance.
        Raises HTTPException if user has no credits.
        """
        user = await self.user_repo.get_user_by_id(conn, user_id)
        if not user or user["credits"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Not enough credits. Please try again tomorrow or purchase more."
            )
        
        updated_credits = user["credits"] - 1
        await self.user_repo.update_user_credits(conn, user_id, updated_credits)
        return updated_credits


    async def get_or_create_user(self, conn: asyncpg.Connection, email: str, name: str, picture: str):
        user = await self.user_repo.get_user_by_email(conn, email)
        if not user:
            # Ensure custom_id uniqueness (minimal check for now)
            custom_id_exists = True
            generated_custom_id = ""
            while custom_id_exists:
                generated_custom_id = self._generate_custom_id()
                existing_user_with_id = await self.user_repo.get_user_by_custom_id(conn, generated_custom_id)
                if not existing_user_with_id:
                    custom_id_exists = False

            initial_credits = 1
            today = date.today()
            user = await self.user_repo.create_user(
                conn, email, generated_custom_id, name, picture, role="MEMBER",
                credits=initial_credits, last_credit_grant_date=today
            )
        else:
            # Check and grant daily credit for existing user
            # Convert last_credit_grant_date from DB (datetime) to date object for comparison
            # Handle potential None for last_credit_grant_date if it was previously null or not set
            last_grant_date_db = user["last_credit_grant_date"]
            if isinstance(last_grant_date_db, datetime):
                last_grant_date_obj = last_grant_date_db.date()
            elif isinstance(last_grant_date_db, date):
                last_grant_date_obj = last_grant_date_db
            else: # Assume it's None or invalid, treat as if never granted to trigger a grant
                last_grant_date_obj = date(1970, 1, 1) # A very old date

            updated_credits = await self._check_and_grant_daily_credit(conn, user["id"], user["credits"], last_grant_date_obj)
            # Re-fetch or update user dict to reflect new credits
            user = await self.user_repo.get_user_by_id(conn, user["id"]) # Re-fetch to get latest state
            
        return user

    async def update_user_by_admin(self, conn: asyncpg.Connection, user_id: int, name: str, role: str, credits: int):
        """
        Updates user information (name, role, credits) by an admin.
        """
        updated_user = await self.user_repo.update_user(conn, user_id, name, role, credits)
        return updated_user

    async def delete_user_by_admin(self, conn: asyncpg.Connection, user_id: int) -> bool:
        """
        Deletes a user by their ID by an admin.
        """
        deleted_count = await self.user_repo.delete_user(conn, user_id)
        return deleted_count > 0
