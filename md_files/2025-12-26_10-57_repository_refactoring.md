# 2025-12-26_10-57 - Repository Pattern Refactoring

## 1. 개요

본 문서는 API 서버의 데이터베이스 접근 로직을 **리포지토리 패턴(Repository Pattern)** 으로 리팩토링한 내역을 기록합니다. 이 작업의 주된 목적은 '관심사의 분리(Separation of Concerns)' 원칙을 적용하여, 비즈니스 로직(라우터)과 데이터 영속성 로직(DB 쿼리)을 명확하게 분리하는 것입니다.

### 기대 효과
- **유지보수성 향상**: 데이터베이스 관련 코드가 리포지토리 모듈에 집중되어 있어 수정 및 관리가 용이합니다.
- **테스트 용이성 증대**: 라우터 테스트 시, 실제 DB 대신 모의(Mock) 리포지토리를 주입하여 단위 테스트를 쉽게 작성할 수 있습니다.
- **코드 재사용성 증가**: 여러 라우터에서 동일한 데이터베이스 쿼리가 필요할 경우, 해당 리포지토리 메서드를 재사용할 수 있습니다.
- **가독성 및 일관성**: 프로젝트 전반에 걸쳐 일관된 데이터 접근 방식을 적용하여 코드 가독성을 높입니다.

## 2. 변경된 파일 목록

### 생성된 파일
- `app/schemas.py`
- `app/repositories/analysis_repository.py`
- `app/dependencies/repositories.py`

### 수정된 파일
- `app/repositories/users_repository.py`
- `app/routers/user_router.py`

## 3. 세부 변경 내역

### 3.1. `app/schemas.py` (생성)
- **목적**: 데이터베이스 모델과 API 응답/요청 본문의 형태를 정의하는 Pydantic 스키마를 중앙에서 관리합니다.
- **주요 내용**:
    - `UserBase`, `UserCreate`, `User` 등 사용자 관련 스키마를 정의했습니다.
    - `AnalysisResultBase`, `AnalysisResult` 등 분석 결과 관련 스키마를 정의했습니다.
    - 이를 통해 API의 명세를 명확히 하고, 타입 안정성을 강화했습니다.

### 3.2. `app/repositories/users_repository.py` (수정)
- **목적**: 사용자(users) 테이블에 대한 모든 CRUD(Create, Read, Update, Delete) 작업을 캡슐화합니다.
- **주요 내용**:
    - 제공된 코드로 파일 내용을 업데이트하여, 사용자 관련 데이터베이스 로직을 `UserRepository` 클래스로 통합했습니다.

### 3.3. `app/repositories/analysis_repository.py` (생성)
- **목적**: 분석 결과(analysis_results) 테이블에 대한 데이터 접근 로직을 분리합니다.
- **주요 내용**:
    - `AnalysisRepository` 클래스를 생성했습니다.
    - 기존에 `user_router.py`에 있던 '사용자의 분석 기록 조회' SQL 쿼리를 `get_analysis_history_by_user_id` 메서드로 이전했습니다.
    - 쿼리 결과를 Pydantic 모델(`AnalysisResult`)로 변환하여 반환하도록 구현했습니다.

### 3.4. `app/dependencies/repositories.py` (생성 및 수정)
- **목적**: 생성된 리포지토리들을 FastAPI의 의존성 주입(Dependency Injection) 시스템을 통해 라우터에 제공합니다.
- **주요 내용**:
    - DB 커넥션을 받아 `UserRepository` 인스턴스를 생성하는 `get_user_repository` 함수를 추가했습니다.
    - DB 커넥션을 받아 `AnalysisRepository` 인스턴스를 생성하는 `get_analysis_repository` 함수를 추가했습니다.

### 3.5. `app/routers/user_router.py` (수정)
- **목적**: 라우터가 더 이상 데이터베이스에 직접 접근하지 않고, 리포지토리를 통해 데이터를 조회하도록 변경합니다.
- **주요 내용**:
    - `/profile` 엔드포인트에서 `Depends(get_db_connection)` 의존성을 제거했습니다.
    - 대신 `analysis_repo: AnalysisRepository = Depends(get_analysis_repository)`를 추가하여 `AnalysisRepository`를 주입받도록 수정했습니다.
    - 직접 실행되던 SQL 쿼리 부분을 `await analysis_repo.get_analysis_history_by_user_id(...)` 호출로 변경하여, 코드를 단순화하고 가독성을 높였습니다.

