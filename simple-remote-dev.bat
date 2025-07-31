@echo off
echo ========================================
echo 간단한 원격 개발 환경 시작
echo ========================================
echo.

echo 1. Docker 개발 환경 시작...
docker-compose -f docker-compose.remote-dev.yml up --build -d

echo.
echo 2. 컨테이너 상태 확인...
docker-compose -f docker-compose.remote-dev.yml ps

echo.
echo 3. IP 주소 확인...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%i
    set IP=!IP: =!
    echo IP 주소: !IP!
)

echo.
echo ========================================
echo 원격 개발 환경이 시작되었습니다!
echo ========================================
echo.
echo 접속 정보:
echo - 웹 애플리케이션: http://%IP%:5000
echo - PostgreSQL: %IP%:5432
echo - Redis: %IP%:6379
echo.
echo 개발 워크플로우:
echo 1. 로컬에서 코드 수정
echo 2. git add . && git commit -m "수정사항" && git push
echo 3. 서버에서 git pull && docker-compose restart web
echo.
echo 또는 자동 동기화:
echo - watch-and-restart.sh 실행 (서버에서)
echo.
echo ======================================== 