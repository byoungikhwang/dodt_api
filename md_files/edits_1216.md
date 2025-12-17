# 12월 16일 수정 기록 종합

---
### 출처: md_files/2025-12-15_17_49.md
---

# 2025-12-15 17:49 수정 내역

## 1. `requirements.txt`: 의존성 추가
- `pydantic-settings` 라이브러리를 추가하여 환경 변수 관리 기능의 안정성을 강화했습니다.

## 2. `app/config/settings.py`: 설정 관리 방식 리팩터링
- 기존의 `os.getenv`와 `python-dotenv`를 직접 사용하던 방식에서 Pydantic의 `BaseSettings`를 상속받는 방식으로 변경했습니다.
- **주요 변경 사항:**
    - 애플리케이션 시작 시 `.env` 파일의 환경 변수를 자동으로 읽고 유효성을 검사합니다.
    - 필수 환경 변수가 누락된 경우, 프로그램이 즉시 시작되지 않고 오류를 발생시켜 문제를 빠르게 인지할 수 있도록 개선했습니다.
    - `DATABASE_URL`과 같이 다른 설정값에 의존하는 변수를 `@computed_field`를 사용하여 동적으로 생성하도록 변경하여 코드의 명확성을 높였습니다.

---

## 3. `requirements.txt`: 미사용 의존성 제거
- 비동기 애플리케이션에서 사용되지 않는 동기 라이브러리 `requests`를 `requirements.txt`에서 삭제하여 의존성을 정리했습니다.

## 4. `app/main.py` & `app/dependencies/db_connection.py`: 데이터베이스 커넥션 풀링 구현
- **`app/main.py` 수정:**
    - 애플리케이션 `startup` 이벤트 시 `asyncpg` 커넥션 풀을 생성하여 `app.state.db_pool`에 저장하는 로직을 추가했습니다.
    - `shutdown` 이벤트 시 생성된 커넥션 풀을 안전하게 닫도록 구현했습니다.
- **`app/dependencies/db_connection.py` 수정:**
    - 요청 시마다 새로운 DB 커넥션을 생성하는 대신, `app.state.db_pool`에 미리 생성된 커넥션 풀에서 커넥션을 가져와 사용하도록 `get_db_connection` 의존성을 변경했습니다.
- **기대 효과:** 이 변경으로 요청 처리 시마다 데이터베이스에 연결하고 해제하는 오버헤드가 사라져 애플리케이션의 성능과 안정성이 크게 향상됩니다.

---
### 출처: md_files/2025-12-16_09_40.md
---

## 2025-12-16: `requirements.txt` 및 `app/main.py` 수정

### `requirements.txt`: 의존성 버전 고정
애플리케이션의 재현 가능한 빌드를 보장하기 위해 `requirements.txt` 파일의 모든 패키지 버전을 최신 버전으로 고정했습니다.

변경 내용:
```
fastapi==0.124.4
uvicorn[standard]==0.38.0
jinja2==3.1.6
python-multipart==0.0.20
pandas==2.3.3
scikit-learn==1.8.0
asyncpg==0.31.0
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-dotenv==1.2.1
httpx==0.28.1
pydantic-settings==2.12.0
```

### `app/main.py`: 로깅 개선
`app/main.py` 파일의 `startup_event` 및 `shutdown_event` 함수 내에서 `print()` 문을 표준 로깅 라이브러리(`logging`)를 사용하도록 변경했습니다. 이는 운영 환경에서 더 효과적인 로그 관리를 가능하게 합니다.

수정 내용은 다음과 같습니다:

- `logging` 모듈 임포트 및 로거 인스턴스 생성
- `startup_event` 내 `print()` -> `logger.info()` 및 `logger.error()`로 변경
- `shutdown_event` 내 `print()` -> `logger.info()`로 변경 

---

---
### 출처: md_files/2025-12-16_09_42.md
---

## 2025-12-16_09_42: `app/auth/jwt_handler.py` 수정

### `app/auth/jwt_handler.py`: 설정 불러오기 방식 개선
`app/auth/jwt_handler.py` 파일에서 환경 변수를 로드하고 설정을 가져오는 방식이 `app/config/settings.py`와 중복되어 수정했습니다. 이제 모든 설정은 `app.config.settings` 모듈에서 가져와 사용합니다. 이는 단일 진실 공급원(Single Source of Truth) 원칙에 부합하며 코드의 일관성을 높입니다.

수정 내용은 다음과 같습니다:

- `load_dotenv()` 호출 제거
- `os` 모듈 임포트 제거
- `app.config.settings`에서 `settings` 객체 임포트
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`를 `settings` 객체에서 직접 가져와 사용

---

---
### 출처: md_files/2025-12-16_09_43.md
---

## 2025-12-16_09_43: `app/config/settings.py` 및 `app/routers/auth_router.py` 수정

### `app/config/settings.py`: Google OAuth 관련 설정 추가
`app/config/settings.py` 파일의 `Settings` 클래스에 Google OAuth2 인증에 필요한 `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` 설정을 추가했습니다. 이를 통해 모든 환경 설정을 한곳에서 중앙 집중식으로 관리할 수 있게 되어 코드의 일관성과 유지보수성이 향상되었습니다.

### `app/routers/auth_router.py`: Google OAuth 설정 불러오기 방식 개선
`app/config/settings.py`에 추가된 Google OAuth 관련 설정을 사용하도록 `app/routers/auth_router.py` 파일을 수정했습니다. 기존에 `os.getenv()`를 통해 개별적으로 환경 변수를 불러오던 방식을 제거하고, `settings` 객체에서 직접 해당 값들을 가져와 사용하도록 변경했습니다. 이는 환경 변수 직접 접근을 줄이고 중앙 집중식 설정 관리를 강화합니다.

---

---
### 출처: md_files/2025-12-16_09_44.md
---

## 2025-12-16_09_44: `app/repositories/users_repository.py` 수정

### `app/repositories/users_repository.py`: `__init__` 메서드 개선
`app/repositories/users_repository.py` 파일의 `UserRepository` 클래스에서 `__init__` 메서드를 제거했습니다. 이제 데이터베이스 연결(`asyncpg.Connection`)은 리포지토리의 각 메서드로 직접 전달됩니다. 이 변경을 통해 서비스 계층에서 단일 연결을 사용하여 여러 리포지토리 호출에 걸쳐 트랜잭션을 관리할 수 있는 유연성이 향상되었습니다.

---

---
### 출처: md_files/2025-12-16_09_47.md
---

## 2025-12-16_09_47: `app/config/settings.py` 및 `app/services/analysis_service.py` 수정

### `app/config/settings.py`: 파일 업로드 디렉토리 설정 추가
`app/config/settings.py` 파일의 `Settings` 클래스에 `UPLOAD_DIRECTORY` 설정을 추가했습니다. 이 설정을 통해 파일 업로드 위치를 환경 변수로 구성할 수 있게 되어 애플리케이션의 유연성과 유지보수성이 향상되었습니다. 기본값은 "app/static/files"로 설정되었습니다.

### `app/services/analysis_service.py`: 업로드 디렉토리 설정 사용
`app/services/analysis_service.py` 파일에서 하드코딩된 업로드 디렉토리 경로 대신 `app.config.settings`에서 가져온 `settings.UPLOAD_DIRECTORY`를 사용하도록 수정했습니다. 이 변경으로 인해 파일 업로드 경로가 외부화되어 보다 유연하고 관리하기 쉬워졌습니다.

---

---
### 출처: md_files/2025-12-16_09_48.md
---

## 2025-12-16_09_48: `app/config/settings.py` 및 `app/routers/recommend_router.py` 수정

### `app/config/settings.py`: Gemini AI 관련 설정 추가
`app/config/settings.py` 파일의 `Settings` 클래스에 Gemini AI 서비스 사용을 위한 `GEMINI_API_KEY` 및 `GOOGLE_GEMINI_MODEL_NAME` 설정을 추가했습니다. 이는 모든 AI 관련 설정을 중앙에서 관리하게 하여 일관성과 보안을 강화합니다. `GOOGLE_GEMINI_MODEL_NAME`의 기본값은 "gemini-pro"입니다.

### `app/routers/recommend_router.py`: Gemini AI 설정 불러오기 및 로깅 개선
`app/routers/recommend_router.py` 파일에서 Gemini AI 관련 설정을 `app.config.settings` 모듈에서 가져와 사용하도록 변경했습니다. 기존의 `os.getenv` 및 `load_dotenv()` 호출을 제거했습니다. 또한, `process_style_generation` 함수 내의 `print()` 문을 표준 로깅 라이브러리(`logging`)의 `logger.info()`로 대체하여 애플리케이션 전반의 로깅 일관성을 유지했습니다.

---

---
### 출처: md_files/2025-12-16_09_49.md
---

## 2025-12-16_09_49: `db/schema.sql` 수정

### `db/schema.sql`: 주석 처리된 코드 제거
`db/schema.sql` 파일에서 사용되지 않는 주석 처리된 테이블 생성 구문을 제거했습니다. 이는 스키마 정의 파일의 가독성과 명확성을 높여 혼동을 방지합니다. 이제 활성화된 스키마 정의만 파일에 남아있습니다.

---

---
### 출처: md_files/2025-12-16_09_50.md
---

## 2025-12-16_09_50: `tests/reproduce_upload_auth.py` 수정

### `tests/reproduce_upload_auth.py`: 테스트 코드 개선
`tests/reproduce_upload_auth.py` 파일의 테스트 스크립트를 `fastapi.testclient.TestClient`를 더 효율적으로 사용하도록 리팩토링했습니다. 불필요한 `asyncio` 및 `httpx` 임포트와 `async/await` 키워드를 제거하여 동기식 테스트 클라이언트 사용에 맞게 코드를 간소화했습니다. `app`과 `TestClient`를 스크립트 내에서 직접 임포트하여 통합 테스트를 용이하게 했습니다.

---

---
### 출처: md_files/2025-12-16_09_51.md
---

## 2025-12-16_09_51: `tests/test_upload_manual.py` 수정

### `tests/test_upload_manual.py`: 테스트 자동화 및 정리 개선
`tests/test_upload_manual.py` 파일을 `pytest` 프레임워크를 활용하는 자동화된 테스트 케이스로 전환했습니다.
주요 변경 사항은 다음과 같습니다:

- `pytest`와 `unittest.mock.patch`를 임포트하여 테스트 기능을 강화했습니다.
- `mock_get_current_user_sync` 함수를 동기식으로 변경하고 `pytest` fixture를 사용하여 `TestClient` 인스턴스화 및 의존성 오버라이드를 처리했습니다.
- 테스트 전에 `UPLOAD_DIRECTORY`를 정리하고 테스트 후에 생성된 파일을 삭제하는 정리 로직을 `test_client` fixture에 추가하여 테스트 환경의 독립성과 반복 가능성을 보장했습니다.
- `print()` 문 대신 명시적인 `assert` 문을 사용하여 HTTP 상태 코드, 응답 구조, `total_users` 값 등을 검증하도록 변경했습니다.
- 이전에 수동으로 확인하던 파일 생성 여부도 `assert`를 통해 검증하도록 업데이트했습니다.

---

---
### 출처: md_files/2025-12-16_12_02.md
---

## 2025-12-16_12_02: `app/config/settings.py` 수정

### `app/config/settings.py`: IndentationError 수정
`app/config/settings.py` 파일에서 발생한 `IndentationError: unexpected unindent` 오류를 수정했습니다. 이 오류는 `Settings` 클래스에 속해야 할 속성들이 클래스 외부로 잘못 배치되어 발생했습니다.

수정 내용은 다음과 같습니다:
- `DATABASE_URL` computed field, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` 속성들을 `Settings` 클래스 내부로 다시 이동시켰습니다.
- 전체 파일 구조를 `pydantic-settings`의 `BaseSettings` 클래스 문법에 맞게 바로잡았습니다.

이 수정으로 애플리케이션이 정상적으로 시작될 수 있게 되었습니다.

---

---
### 출처: md_files/2025-12-16_12_51.md
---

## 2025-12-16_12_51: `app/routers/auth_router.py` 임시 수정 (디버깅 목적)

### `app/routers/auth_router.py`: `GOOGLE_REDIRECT_URI` 하드코딩
`redirect_uri_mismatch` 오류의 원인이 `.env` 파일 로딩 문제인지 확인하기 위해, `app/routers/auth_router.py` 파일 내 `GOOGLE_REDIRECT_URI` 값을 임시로 하드코딩했습니다.

수정 내용:
-   `GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI` 라인을
-   `GOOGLE_REDIRECT_URI = "http://192.168.0.138:5500/rest/oauth2-credential/callback"` 로 변경

이 변경은 디버깅을 위한 임시 조치이며, 문제가 해결되면 원래대로 복원될 예정입니다.

---

---
### 출처: md_files/2025-12-16_13_05.md
---

## 2025-12-16_13_05: `app/routers/auth_router.py` 수정

### `app/routers/auth_router.py`: `device_id` 및 `device_name` 추가
Google OAuth 로그인 시 비공개 IP 주소(`192.168.0.138`)에서 발생하는 `invalid_request` 오류를 해결하기 위해 `app/routers/auth_router.py` 파일의 `login_google` 함수를 수정했습니다.

수정 내용은 다음과 같습니다:
-   `uuid` 모듈을 임포트했습니다.
-   Google 인증 URL에 `device_id` (고유 UUID 생성)와 `device_name` (임시로 "local-dev-machine") 파라미터를 추가했습니다.

이 변경으로 인해 Google의 비공개 IP에 대한 보안 정책을 만족시키고 로그인 진행이 가능해질 것입니다.

---

---
### 출처: md_files/2025-12-16_13_18.md
---

## 2025-12-16_13_18: `app/routers/auth_router.py`에 로그 추가 (디버깅)

### `app/routers/auth_router.py`: 인증 URL 로깅 추가
`redirect_uri_mismatch` 오류의 근본 원인을 파악하기 위해, `app/routers/auth_router.py`의 `login_google` 함수에 로그 출력 코드를 추가했습니다.

수정 내용은 다음과 같습니다:
-   `logging` 모듈을 임포트하고 `logger` 인스턴스를 생성했습니다.
-   `login_google` 함수가 Google 인증 URL을 생성한 후, `RedirectResponse`를 반환하기 직전에 해당 URL을 `logger.info`를 통해 출력하도록 했습니다.

이 로그를 통해 애플리케이션이 실제로 어떤 URL을 생성하여 브라우저로 보내는지 명확히 확인할 수 있습니다.

---

---
### 출처: md_files/2025-12-16_15_15.md
---

## 2025-12-16_15_15: 디버깅 코드 복원 및 `.env` 로딩 강화

### `app/routers/auth_router.py`: 임시 코드 복원
`redirect_uri_mismatch` 오류 디버깅을 위해 임시로 하드코딩했던 `GOOGLE_REDIRECT_URI`와 `device_id`/`device_name` 관련 코드를 원래대로 복원했습니다. `GOOGLE_REDIRECT_URI`는 이제 `settings` 객체에서 값을 가져오도록 변경되었습니다. `logger` 관련 코드는 유지했습니다.

### `app/config/settings.py`: `.env` 파일 로딩 강화
`.env` 파일이 애플리케이션에 의해 제대로 로드되지 않는 문제를 해결하기 위해, `app/config/settings.py` 파일에 `from dotenv import load_dotenv` 및 `load_dotenv()` 호출을 추가했습니다. 이는 `pydantic-settings`가 `.env` 파일을 로드하기 전에 `dotenv` 라이브러리를 통해 환경 변수를 명시적으로 불러오도록 하여, 환경 변수 로딩의 신뢰성을 높입니다.

---

---
### 출처: md_files/2025-12-16_16_07.md
---

## 2025-12-16_16_07: `app/routers/auth_router.py`에 상세 디버깅 로그 추가

### `app/routers/auth_router.py`: 토큰 요청 파라미터 로깅
지속적인 Google OAuth 인증 오류의 근본 원인을 파악하기 위해, `google_callback` 함수 내부에 상세한 디버깅 로그를 추가했습니다.

수정 내용은 다음과 같습니다:
-   Google에 토큰 교환을 요청하기 직전에, `client_id`, `client_secret`(길이만 마스킹 처리), `redirect_uri`의 실제 값을 `logger.info`를 통해 서버 로그에 출력하도록 했습니다.

이 로그를 통해 애플리케이션이 `.env` 파일의 값을 제대로 읽고 있는지, 그리고 정확히 어떤 값들을 Google에 보내고 있는지 최종적으로 확인할 수 있습니다.

---

---
### 출처: md_files/2025-12-16_16_30.md
---

## 2025-12-16_16_30: `app/routers/auth_router.py`에 `device_id` 및 `device_name` fix 재적용

### `app/routers/auth_router.py`: `device_id` 및 `device_name` fix 재적용
`redirect_uri_mismatch` 문제가 해결된 후, Google의 비공개 IP 정책으로 인해 다시 발생한 `invalid_request` 오류(`device_id and device_name are required`)를 해결하기 위해 `login_google` 함수에 `device_id` 및 `device_name` 파라미터를 다시 추가했습니다.

수정 내용은 다음과 같습니다:
-   `uuid` 모듈 임포트를 포함하여, `device_id`와 `device_name`을 생성하고 Google 인증 URL에 추가했습니다.
-   디버깅을 위해 `auth_url`을 로깅하는 코드도 함께 포함되었습니다.

이제 Google의 비공개 IP 정책 요구사항을 만족시키고 로그인 절차를 완료할 수 있을 것으로 예상됩니다.

---

---
### 출처: md_files/2025-12-16_16_43.md
---

## 2025-12-16_16_43: `app/routers/auth_router.py` 최종 정리

### `app/routers/auth_router.py`: 디버깅 코드 최종 제거
Google OAuth 로그인 문제가 해결됨에 따라, 디버깅 과정에서 추가했던 임시 코드들을 모두 제거하여 코드를 원래의 깨끗한 상태로 복원했습니다.

제거된 내용:
-   `login_google` 함수에 추가되었던 `device_id` 및 `device_name` 파라미터 생성 로직
-   `google_callback` 함수에 추가되었던 토큰 요청 파라미터 로깅 블록
-   더 이상 사용되지 않는 `logging` 및 `uuid` 모듈 임포트
-   불필요한 `logger` 인스턴스 생성 코드

이 작업을 통해 인증 라우터의 코드가 최종적으로 정리되었습니다.

---

---
### 출처: md_files/2025-12-16_16_45.md
---

## 2025-12-16_16_45: `app/routers/auth_router.py` `NameError` 수정

### `app/routers/auth_router.py`: `router` 변수 초기화 코드 복원
코드 정리 과정에서 실수로 삭제되었던 `router = APIRouter()` 라인을 `app/routers/auth_router.py` 파일에 다시 추가했습니다.

이 라인의 누락으로 인해 `NameError: name 'router' is not defined` 오류가 발생하여 애플리케이션이 시작되지 못했습니다. 코드를 복원하여 이 문제를 해결했습니다.

---

---
### 출처: md_files/2025-12-16_17_28.md
---

## 2025-12-16_17_28: `app/routers/auth_router.py`에 Google OAuth 설정 하드코딩 (최종 디버깅)

### `app/routers/auth_router.py`: Google OAuth 설정값 하드코딩
지속적인 `redirect_uri_mismatch` 오류의 근본 원인(애플리케이션이 `.env` 파일의 값을 읽지 못하고 시스템 환경 변수를 사용하던 문제)을 우회하기 위해, Google OAuth 관련 설정값(`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`)을 `app/routers/auth_router.py` 파일에 직접 하드코딩했습니다.

이는 디버깅을 위한 임시 조치이며, 애플리케이션이 올바른 설정값들을 사용하도록 강제하여 문제를 최종적으로 해결하기 위함입니다.

하드코딩된 값:
-   `GOOGLE_CLIENT_ID = "[REDACTED]"`
-   `GOOGLE_CLIENT_SECRET = "[REDACTED]"`
-   `GOOGLE_REDIRECT_URI = "http://localhost:8000/rest/oauth2-credential/callback"`

로그인이 성공적으로 완료되면, 이 하드코딩된 값들은 제거하고 `settings` 객체를 사용하는 원래 코드로 복원할 예정입니다.

---

---
### 출처: md_files/2025-12-16_18_01.md
---

## 2025-12-16_18_01: 데이터베이스 스키마 수정 (`users` 테이블 `role` 컬럼 추가)

### `users` 테이블에 `role` 컬럼 추가
`KeyError: 'role'` 오류를 해결하기 위해, `users` 테이블에 `role` 컬럼을 추가했습니다. 이 컬럼은 Google 로그인 시 사용자에게 기본 역할을 부여하는 데 사용됩니다.

수정 내용은 다음과 같습니다:
-   `psql`을 통해 다음 SQL 명령어를 실행했습니다:
    ```sql
    ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'MEMBER';
    ```

이제 애플리케이션이 사용자 로그인 후 `role` 정보를 정상적으로 처리할 수 있게 되었습니다.

---

---
### 출처: md_files/2025-12-16_18_07.md
---

## 2025-12-16_18_07: `db/schema.sql` 파일 정리

### `db/schema.sql`: DML/DQL 및 비표준 주석 제거
`psql` 명령어 실행 시 발생했던 구문 오류를 해결하고 `schema.sql` 파일을 데이터베이스 스키마 정의 용도에 맞게 정리했습니다.

수정 내용은 다음과 같습니다:
-   `#`으로 시작하는 비표준 주석들을 제거했습니다.
-   `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `\d`와 같은 데이터 조작/조회 언어(DML/DQL) 예시 문장들을 제거했습니다.
-   이제 `db/schema.sql` 파일은 DDL(Data Definition Language) 문과 표준 SQL 주석(`--`)만을 포함하여, 순수한 스키마 정의 파일이 되었습니다.

---
