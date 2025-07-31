@echo off
REM FS Master Web Application 로컬 실행 스크립트 (Windows)

echo 🚀 FS Master Web Application 로컬 실행 중...

REM Python 가상환경 확인
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
echo 🔄 가상환경 활성화...
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📦 의존성 설치 중...
pip install -r requirements.txt

REM db_connection_test 패키지 설치
echo 📦 db_connection_test 패키지 설치 중...
cd db_connection_test
pip install -e .
cd ..

REM PostgreSQL 확인
echo 🗄️ PostgreSQL 연결 확인...
python -c "import psycopg2; psycopg2.connect('postgresql://postgres:postgres123@localhost/fs_master_web')" 2>nul
if errorlevel 1 (
    echo ❌ PostgreSQL이 실행되지 않았습니다.
    echo 📋 PostgreSQL 설치 및 실행 방법:
    echo   1. https://www.enterprisedb.com/downloads/postgres-postgresql-downloads 에서 다운로드
    echo   2. 설치 시 비밀번호를 'postgres123'으로 설정
    echo   3. 서비스 시작 후 다시 실행
    pause
    exit /b 1
)

REM 데이터베이스 테이블 생성
echo 🗃️ 데이터베이스 테이블 생성 중...
python app.py --setup-only

REM 웹 애플리케이션 시작
echo 🌐 웹 애플리케이션 시작...
python app.py --host 0.0.0.0 --port 5000

pause 