from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Persona Customer Survey"
    PROJECT_VERSION: str = "0.9.0"

    # The .env file will be loaded automatically by BaseSettings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tdd"

    # Using a computed_field for the database URL
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # This tells pydantic to load variables from a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
