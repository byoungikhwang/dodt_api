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
