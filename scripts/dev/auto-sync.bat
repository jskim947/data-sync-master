@echo off
echo ========================================
echo Git 자동 동기화 시스템
echo ========================================
echo.

echo 1. 개발 환경 시작...
call start-dev.bat

echo.
echo 2. 자동 동기화 모니터링 시작...
echo 클라이언트에서 Git 푸시하면 자동으로 반영됩니다.
echo.

:monitor_loop
echo [%date% %time%] Git 변경사항 확인 중...
git fetch origin main

if %errorlevel% neq 0 (
    echo Git fetch 실패, 재시도 중...
    timeout /t 5 /nobreak >nul
    goto monitor_loop
)

git status --porcelain | findstr /c:" M " /c:" A " /c:" D " >nul
if %errorlevel% equ 0 (
    echo 변경사항 감지! 업데이트 중...
    git pull origin main
    docker-compose -f ..\..\docker\docker-compose.dev.yml restart web
    echo [%date% %time%] 업데이트 완료!
) else (
    echo 변경사항 없음
)

echo 5초 후 다시 확인...
timeout /t 5 /nobreak >nul
goto monitor_loop 