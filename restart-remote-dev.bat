@echo off
echo ========================================
echo FS Master 원격 개발 환경 재시작
echo ========================================
echo.

echo 1. 웹 애플리케이션 재시작...
docker-compose -f docker-compose.remote-dev.yml restart web

echo.
echo 2. 컨테이너 상태 확인...
docker-compose -f docker-compose.remote-dev.yml ps

echo.
echo 3. 로그 확인 (Ctrl+C로 종료)...
echo ========================================
docker-compose -f docker-compose.remote-dev.yml logs -f web

echo.
echo ========================================
echo 재시작이 완료되었습니다!
echo 웹 애플리케이션: http://localhost:5000
echo ======================================== 