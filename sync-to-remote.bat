@echo off
echo ========================================
echo 로컬 -> 원격 서버 자동 동기화
echo ========================================
echo.

set REMOTE_HOST=10.150.2.150
set REMOTE_PATH=/path/to/data-sync-master
set LOCAL_PATH=.

echo 1. 변경된 파일 확인...
git status --porcelain

echo.
echo 2. 원격 서버로 파일 동기화...
echo 대상: %REMOTE_HOST%:%REMOTE_PATH%

echo.
echo 3. rsync를 사용한 동기화 (Linux/Mac 환경에서만 작동)
echo Windows에서는 다음 방법을 사용하세요:
echo - Git push 후 서버에서 git pull
echo - WinSCP 등의 도구 사용
echo - WSL에서 rsync 사용

echo.
echo 4. Git 기반 동기화 (권장)
echo 로컬에서: git add . && git commit -m "자동 동기화" && git push
echo 서버에서: git pull && docker-compose -f docker-compose.remote-dev.yml restart web

echo.
echo ========================================
echo 동기화 완료!
echo 원격 서버: http://%REMOTE_HOST%:5000
echo ======================================== 