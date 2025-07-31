@echo off
echo ========================================
echo 운영 환경 시작
echo ========================================
echo.

echo 1. 운영용 이미지 확인...
docker images | findstr data-sync-web:prod >nul
if %errorlevel% neq 0 (
    echo 운영용 이미지가 없습니다. 먼저 빌드하세요:
    echo .\scripts\prod\build-prod.bat
    pause
    exit /b 1
)

echo.
echo 2. 기존 운영 컨테이너 정리...
docker-compose -f ..\..\docker\docker-compose.prod.yml down

echo.
echo 3. 운영 환경 시작...
docker-compose -f ..\..\docker\docker-compose.prod.yml up -d

echo.
echo 4. 서비스 상태 확인...
docker-compose -f ..\..\docker\docker-compose.prod.yml ps

echo.
echo 5. 운영 로그 확인...
echo 로그를 확인하려면: docker-compose -f ..\..\docker\docker-compose.prod.yml logs -f web
echo.

echo ========================================
echo 운영 환경 시작 완료!
echo ========================================
echo.
echo 접속 정보:
echo - 웹 애플리케이션: http://localhost:5000
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo.
echo 운영 환경은 최적화된 이미지를 사용합니다.
echo ======================================== 