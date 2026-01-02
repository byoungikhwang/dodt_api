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

    # The .env file will be loaded automatically by BaseSettings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    
    # [수정 전] .env 파일의 변수명(POSTGRES_SERVER)과 불일치
    # POSTGRES_HOST: str = "localhost"
    
    # [수정 후] .env 파일의 키값인 db_host로 변수명 통일
    db_host: str
    
    db_port: int
    
    # [수정 전] .env 값(main_db)과 다른 기본값 사용으로 혼동 우려
    # POSTGRES_DB: str = "tdd"
    
    # [수정 후] 기본값을 제거하거나 .env와 맞춥니다. (여기선 타입을 명시하고 기본값은 .env에 위임)
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
        # [수정 전] self.POSTGRES_HOST 사용 (변수명 변경으로 인해 에러 발생 가능성)
        # return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD} @{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        # [수정 후] 변경된 변수명(db_host) 적용 및 asyncpg 프로토콜 명시
        # 참고: 비밀번호에 특수문자가 있을 경우 URL 인코딩이 필요할 수 있으나, 현재는 기본 구조를 유지합니다.
        return f"postgresql://{self.POSTGRES_USER}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.db_host}:{self.db_port}/{self.POSTGRES_DB}"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # [수정 전] Pydantic V1 스타일의 Config 클래스 (Deprecated 예정)
    # class Config:
    #     # This tells pydantic to load variables from a .env file
    #     env_file = ".env"
    #     env_file_encoding = 'utf-8'

    # [수정 후] Pydantic V2 권장 스타일 (model_config 사용)
    # extra='ignore' 옵션은 .env에 정의되었지만 이 클래스에 없는 변수(예: db_host 등)가 있어도 에러를 내지 않도록 합니다.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
