-- 1. 벡터 확장 기능 활성화 (RAG용)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 사용자 테이블 (schema.sql)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    picture VARCHAR(512),
    role VARCHAR(50) DEFAULT 'MEMBER', -- Added role column
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 분석 결과 테이블 (schema.sql)
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    filename VARCHAR(255),
    filelink VARCHAR(512),
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 스타일 요청 로그 테이블 (n8n 연동용 추가)
CREATE TABLE IF NOT EXISTS style_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50), -- users 테이블의 ID 또는 Email 저장
    prompt_text TEXT NOT NULL,
    generated_style VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 5. 샘플 데이터 삽입 
INSERT INTO users (name, email, age) VALUES ('홍길동', 'hong@example.com', 25);

-- 6.모든 데이터 가져오기: 
SELECT * FROM users;

-- 7. 특정 유저 삭제
DELETE FROM users WHERE email = 'user@example.com';

-- 8. 데이터 수정   
UPDATE users SET name = '새이름' WHERE email = '';


--1. 컬럼 추가 (ADD) 기존 테이블에 새로운 정보를 담을 칸을 추가합니다.
    #예제 (전화번호 컬럼 추가): 
ALTER TABLE users ADD phone VARCHAR(20);

--2. 컬럼 삭제 (DROP)더 이상 필요 없는 컬럼을 제거합니다.
    #예제 (나이 컬럼 삭제): 
ALTER TABLE users DROP COLUMN age;

--3. 컬럼 수정 (MODIFY / ALTER) 컬럼의 데이터 타입(글자 수 등)이나 제약 조건을 변경합니다. 
    # 예제 (이름 글자 수를 100자로 변경): 
ALTER TABLE users MODIFY name VARCHAR(100);

--4. 컬럼 이름 변경 (RENAME) 기존 컬럼의 이름을 바꿉니다.
# 예제 (email을 user_email로 변경): 
ALTER TABLE users RENAME COLUMN email TO user_email;

--5. 테이블 이름 변경 (RENAME TO) 테이블 자체의 이름을 바꿉니다.
#예제 (users를 members로 변경): 
ALTER TABLE users RENAME TO members;