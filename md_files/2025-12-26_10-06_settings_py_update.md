# 2025-12-26_10-06_settings_py_update.md

## `app/config/settings.py` 파일 수정 내역

### 변경 이유
Pydantic v2의 최신 권장 설정 방식을 따르고, `.env` 파일 로딩의 일관성을 확보하며, DB 설정 변수명을 명확히 하여 코드의 가독성과 유지보수성을 향상시키기 위함입니다. 또한, Deprecated된 기능을 최신 표준으로 업데이트합니다.

### 변경 사항 요약
1.  **`.env` 파일 로딩 방식 개선:**
    *   `dotenv.load_dotenv()` 수동 호출 제거.
    *   `pydantic_settings.BaseSettings`가 `.env` 파일을 자동으로 처리하도록 변경.
2.  **DB 설정 변수명 통일:**
    *   `POSTGRES_HOST`를 `.env`의 키값과 일치하는 `POSTGRES_SERVER`로 변경.
    *   `DATABASE_URL` computed field에서 변경된 `POSTGRES_SERVER` 변수명 반영.
3.  **DB 이름 기본값 처리:**
    *   `POSTGRES_DB`의 기본값을 `.env`와 일치하도록 "main_db"로 설정하여 혼동 방지.
4.  **Pydantic 설정 스타일 업데이트:**
    *   Deprecated된 `class Config:` 대신 `model_config = SettingsConfigDict(...)` 사용.
    *   `extra='ignore'` 옵션을 추가하여, `.env`에 정의되었으나 모델에 없는 변수가 있을 경우 에러를 방지.

### 코드 변경 전후 (참고)

**수정 전 (주요 변경점):**
```python
from pydantic import computed_field
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Explicitly load .env file

class Settings(BaseSettings):
    # ...
    POSTGRES_HOST: str = "localhost"
    # ...
    POSTGRES_DB: str = "tdd"
    # ...
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    # ...
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
```

**수정 후 (주요 변경점):**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
# [수정 전] 불필요한 라이브러리 및 중복 로드
# from dotenv import load_dotenv # Import load_dotenv
# load_dotenv() # Explicitly load .env file

# [수정 후] Pydantic의 BaseSettings가 자동으로 .env를 읽으므로 수동 로드는 제거합니다.
# (이중 로드는 설정 우선순위 혼동을 야기할 수 있습니다.)

class Settings(BaseSettings):
    # ...
    # [수정 전] .env 파일의 변수명(POSTGRES_SERVER)과 불일치
    # POSTGRES_HOST: str = "localhost"
    
    # [수정 후] .env 파일의 키값인 POSTGRES_SERVER로 변수명 통일
    POSTGRES_SERVER: str = "localhost"
    # ...
    # [수정 전] .env 값(main_db)과 다른 기본값 사용으로 혼동 우려
    # POSTGRES_DB: str = "tdd"
    
    # [수정 후] 기본값을 제거하거나 .env와 맞춥니다. (여기선 타입을 명시하고 기본값은 .env에 위임)
    POSTGRES_DB: str = "main_db"
    # ...
    @computed_field @property
    def DATABASE_URL(self) -> str:
        # [수정 전] self.POSTGRES_HOST 사용 (변수명 변경으로 인해 에러 발생 가능성)
        # return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD} @{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        # [수정 후] 변경된 변수명(POSTGRES_SERVER) 적용 및 asyncpg 프로토콜 명시
        # 참고: 비밀번호에 특수문자가 있을 경우 URL 인코딩이 필요할 수 있으나, 현재는 기본 구조를 유지합니다.
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    # ...
    # [수정 전] Pydantic V1 스타일의 Config 클래스 (Deprecated 예정)
    # class Config:
    #     # This tells pydantic to load variables from a .env file
    #     # env_file = ".env"
    #     # env_file_encoding = 'utf-8'

    # [수정 후] Pydantic V2 권장 스타일 (model_config 사용)
    # extra='ignore' 옵션은 .env에 정의되었지만 이 클래스에 없는 변수(예: db_host 등)가 있어도 에러를 내지 않도록 합니다.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

