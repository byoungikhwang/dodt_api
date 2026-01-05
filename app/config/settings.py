from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from urllib.parse import quote_plus
# [수정 전] 불필요한 라이브러리 및 중복 로드
# from dotenv import load_dotenv # Import load_dotenv
# load_dotenv() # Explicitly load .env file

# [수정 후] Pydantic의 BaseSettings가 자동으로 .env를 읽으므로 수동 로드는 제거합니다.
# (이중 로드는 설정 우선순위 혼동을 야기할 수 있습니다.)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Persona Customer Survey"
    PROJECT_VERSION: str = "0.9.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str = "main_db"

    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    UPLOAD_DIRECTORY: str = "app/static/files"

    GEMINI_API_KEY: str
    GOOGLE_GEMINI_MODEL_NAME: str = "gemini-pro"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Pydantic BaseSettings now uses the correct environment variable names
        return (f"postgresql://{self.POSTGRES_USER}:{quote_plus(self.POSTGRES_PASSWORD)}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
