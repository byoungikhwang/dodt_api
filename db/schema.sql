-- ===============================================
-- 데이터베이스 생성 및 스키마 적용 가이드
-- ===============================================
-- 1. 데이터베이스 생성:
--    이 스크립트는 'main_db'라는 데이터베이스 내에서 실행되어야 합니다.
--    psql (또는 터미널)에서: CREATE DATABASE main_db;
--
-- 2. 스키마 적용:
--    'main_db' 데이터베이스에 연결한 후, 이 스크립트를 실행합니다.
--    psql -h db_postgresql -p 5432 -U admin -d main_db -f db/schema.sql
-- ===============================================

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- ===============================================
-- 테이블: users
-- 설명: 서비스 사용자 정보 저장
-- ===============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    custom_id VARCHAR(10) UNIQUE,
    name VARCHAR(255),
    picture VARCHAR(512),
    role VARCHAR(50) DEFAULT 'MEMBER',
    credits INTEGER DEFAULT 1,
    last_credit_grant_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);



-- CRUD 예제: users
-- C (Create):
-- INSERT INTO users (email, name, picture, role) VALUES ('test@example.com', '테스트유저', 'picture_url', 'MEMBER');
-- R (Read):
 SELECT * FROM users;
 
SELECT * FROM users 

-- UPDATE users SET name = '새이름' WHERE email = 'test@example.com';
-- D (Delete):
-- DELETE FROM users WHERE email = 'test@example.com';

-- ===============================================
-- 테이블: media
-- 설명: 사용자가 생성/업로드하는 미디어(이미지, 비디오) 정보
-- ===============================================
CREATE TABLE IF NOT EXISTS media (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    media_type VARCHAR(50), -- 'image' or 'video'
    url VARCHAR(512) NOT NULL, -- s3 또는 static 경로
    hashtags TEXT[], -- 해시태그 목록 (PostgreSQL 배열)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- CRUD 예제: media
-- C (Create):
-- INSERT INTO media (user_id, title, description, media_type, url, hashtags) VALUES (1, '첫번째 피드', '피드 설명입니다.', 'image', '/static/uploads/image.png', '{"#일상", "#데일리"}');
-- R (Read):
-- -- 모든 미디어 조회
-- SELECT * FROM media ORDER BY created_at DESC;
-- -- 특정 사용자의 미디어 조회
-- SELECT * FROM media WHERE user_id = 1;
-- -- 해시태그로 검색
-- SELECT * FROM media WHERE '#일상' = ANY(hashtags);
-- U (Update):
-- UPDATE media SET description = '수정된 설명' WHERE id = 1;
-- D (Delete):
-- DELETE FROM media WHERE id = 1;

-- ===============================================
-- 테이블: media_likes
-- 설명: 미디어에 대한 사용자의 '좋아요' 관계 저장
-- ===============================================
CREATE TABLE IF NOT EXISTS media_likes (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    media_id INTEGER REFERENCES media(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, media_id)
);

-- CRUD 예제: media_likes
-- C (Create - 좋아요 추가):
-- INSERT INTO media_likes (user_id, media_id) VALUES (1, 1);
-- R (Read):
-- -- 특정 게시물의 좋아요 개수 세기
-- SELECT count(*) FROM media_likes WHERE media_id = 1;
-- -- 특정 사용자가 좋아요를 눌렀는지 확인
-- SELECT EXISTS (SELECT 1 FROM media_likes WHERE user_id = 1 AND media_id = 1);
-- -- 인기순(좋아요순)으로 미디어 정렬
-- SELECT m.*, count(ml.media_id) as like_count FROM media m LEFT JOIN media_likes ml ON m.id = ml.media_id GROUP BY m.id ORDER BY like_count DESC;
-- D (Delete - 좋아요 취소):
-- DELETE FROM media_likes WHERE user_id = 1 AND media_id = 1;


-- ===============================================
-- 기타 테이블
-- ===============================================
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    filename VARCHAR(255),
    filelink VARCHAR(512),
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS style_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50), -- users 테이블의 ID 또는 Email 저장
    prompt_text TEXT NOT NULL,
    generated_style VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 스키마 적용 후, 테이블이 올바르게 생성되었는지 확인하는 쿼리
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

    2 INSERT INTO users (email, custom_id, name, picture, role, credits) VALUES
    3     ('admin@example.com', 'admin_id', 'Admin User', 'https://example.com/admin_pic.jpg', 'ADMIN', 100),
    4     ('user@example.com', 'user_id', 'Test User', 'https://example.com/user_pic.jpg', 'MEMBER', 50)
    5 ON CONFLICT (email) DO UPDATE SET
    6     custom_id = EXCLUDED.custom_id,
    7     name = EXCLUDED.name,
    8     picture = EXCLUDED.picture,
    9     role = EXCLUDED.role,
   10     credits = EXCLUDED.credits;

--    12 -- Sample data for media table
--    13 -- Assuming user IDs 1 and 2 exist from above insertions
   14 INSERT INTO media (user_id, title, description, media_type, url, hashtags) VALUES
   15     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'Admin Image 1', 'First image from admin.', 'image', '/static/uploads/admin_image_01.png', ARRAY['#admin', '#first_upload']),
   16     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'Admin Video 1', 'First video from admin, very popular!', 'video', '/static/uploads/admin_video_01.mp4', ARRAY['#admin', '#video', 
      '#popular'] ),
   17     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'User Image 1', 'A beautiful photo by test user.', 'image', '/static/uploads/user_image_01.png', ARRAY['#user', '#nature']),
   18     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'User Video 1', 'Test user''s awesome clip.', 'video', '/static/uploads/user_video_01.mp4', ARRAY['#user', '#clip'])
   19 ON CONFLICT DO NOTHING; -- Assuming (user_id, title, url) could be a unique constraint, or simply avoid re-insertion for existing data.
   20 
   21 -- Sample data for media_likes table
   22 -- Admin user likes all media
   23 INSERT INTO media_likes (user_id, media_id) VALUES
   24     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Image 1')),
   25     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Video 1')),
   26     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'User Image 1')),
   27     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'User Video 1'));
   28 
   29 -- Test user likes admin's popular video
   30 INSERT INTO media_likes (user_id, media_id) VALUES
   31     ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Video 1'))
   32 ON CONFLICT DO NOTHING; -- Avoid re-insertion for existing likes.

--   위 쿼리 실행 후, FastAPI 애플리케이션을 다시 시작하고 api/media 엔드포인트에 요청을 보내면 정상적으로 데이터가 반환될 것입니다.

 SELECT * FROM media;