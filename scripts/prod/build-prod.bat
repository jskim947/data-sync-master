@echo off
echo ========================================
echo 운영용 이미지 빌드
echo ========================================
echo.

echo 1. 기존 운영 컨테이너 중지...
docker-compose -f ..\..\docker\docker-compose.prod.yml down

echo.
echo 2. 운영용 이미지 빌드...
docker build -f ..\..\docker\Dockerfile.prod -t data-sync-web:prod ..

if %errorlevel% neq 0 (
    echo 이미지 빌드 실패!
    pause
    exit /b 1
)

echo.
echo 3. 빌드된 이미지 확인...
docker images | findstr data-sync-web

echo.
echo ========================================
echo 운영용 이미지 빌드 완료!
echo ========================================
echo.
echo 다음 명령어로 운영 환경을 시작하세요:
echo .\scripts\prod\start-prod.bat
echo ======================================== 