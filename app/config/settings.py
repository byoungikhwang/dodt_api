from pydantic_settings import BaseSettings
from pydantic import computed_field
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Explicitly load .env file

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Persona Customer Survey"
    PROJECT_VERSION: str = "0.9.0"

    # The .env file will be loaded automatically by BaseSettings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tdd"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    UPLOAD_DIRECTORY: str = "app/static/files"

    GEMINI_API_KEY: str
    GOOGLE_GEMINI_MODEL_NAME: str = "gemini-pro"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # This tells pydantic to load variables from a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
