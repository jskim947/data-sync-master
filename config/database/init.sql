-- FS Master Web Application 초기화 스크립트

-- 데이터베이스 생성 (이미 생성됨)
-- CREATE DATABASE fs_master_web;

-- 필요한 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 기본 사용자 권한 설정
GRANT ALL PRIVILEGES ON DATABASE fs_master_web TO postgres;

-- 로그 메시지
DO $$
BEGIN
    RAISE NOTICE 'FS Master Web Application 데이터베이스 초기화 완료';
END $$; 