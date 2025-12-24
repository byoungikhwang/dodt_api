import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_db_connection():
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("db_host")
    port = os.getenv("db_port")
    database = os.getenv("POSTGRES_DB")

    conn = None
    try:
        print(f"Attempting to connect to PostgreSQL at {host}:{port}/{database} as user {user}...")
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("Successfully connected to the database!")
        # Optional: execute a simple query to ensure the connection is active
        # result = await conn.fetchval("SELECT 1")
        # print(f"Query test result: {result}")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
    finally:
        if conn:
            await conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(test_db_connection())
