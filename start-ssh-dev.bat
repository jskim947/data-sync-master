@echo off
echo ========================================
echo SSH 서버 + 개발 환경 시작
echo ========================================
echo.

echo 1. 기존 컨테이너 정리...
docker-compose -f docker-compose.ssh.yml down

echo.
echo 2. SSH 서버 및 개발 환경 시작...
docker-compose -f docker-compose.ssh.yml up --build -d

echo.
echo 3. 컨테이너 상태 확인...
docker-compose -f docker-compose.ssh.yml ps

echo.
echo ========================================
echo SSH 서버 및 개발 환경이 시작되었습니다!
echo ========================================
echo.
echo 접속 정보:
echo - SSH 접속: ssh developer@172.27.64.1 -p 22
echo - 비밀번호: password123
echo - 웹 애플리케이션: http://172.27.64.1:5000
echo - PostgreSQL: 172.27.64.1:5432
echo - Redis: 172.27.64.1:6379
echo.
echo VS Code Remote-SSH 설정:
echo Host: 172.27.64.1
echo Port: 22
echo Username: developer
echo Password: password123
echo.
echo 명령어:
echo - 로그 확인: docker-compose -f docker-compose.ssh.yml logs -f
echo - SSH 재시작: docker-compose -f docker-compose.ssh.yml restart ssh
echo - 종료: docker-compose -f docker-compose.ssh.yml down
echo ======================================== 