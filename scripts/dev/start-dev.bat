@echo off
echo ========================================
echo 개발 환경 시작
echo ========================================
echo.

echo 1. 기존 컨테이너 정리...
docker-compose -f ..\..\docker\docker-compose.dev.yml down

echo.
echo 2. 개발 환경 빌드 및 시작...
docker-compose -f ..\..\docker\docker-compose.dev.yml up --build -d

echo.
echo 3. 서비스 상태 확인...
docker-compose -f ..\..\docker\docker-compose.dev.yml ps

echo.
echo 4. 웹 애플리케이션 로그 확인...
echo 로그를 확인하려면: docker-compose -f ..\..\docker\docker-compose.dev.yml logs -f web
echo.

echo ========================================
echo 개발 환경 시작 완료!
echo ========================================
echo.
echo 접속 정보:
echo - 웹 애플리케이션: http://localhost:5000
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo.
echo 코드 수정 시 자동으로 반영됩니다.
echo ======================================== 