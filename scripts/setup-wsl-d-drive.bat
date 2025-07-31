@echo off
echo ========================================
echo WSL D드라이브 설치 및 Cursor, Docker 설정
echo ========================================
echo.

echo 1. WSL 기능 활성화 중...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
if %errorlevel% neq 0 (
    echo WSL 기능 활성화 실패!
    pause
    exit /b 1
)

echo 2. 가상 머신 플랫폼 활성화 중...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
if %errorlevel% neq 0 (
    echo 가상 머신 플랫폼 활성화 실패!
    pause
    exit /b 1
)

echo 3. WSL2 커널 업데이트 다운로드 중...
echo WSL2 커널 업데이트를 다운로드하고 설치하세요:
echo https://aka.ms/wsl2kernel
echo.
echo 다운로드 후 설치를 완료하고 Enter를 누르세요...
pause

echo 4. WSL 기본 버전을 WSL2로 설정 중...
wsl --set-default-version 2
if %errorlevel% neq 0 (
    echo WSL2 기본 버전 설정 실패!
    pause
    exit /b 1
)

echo 5. D드라이브에 WSL 디렉토리 생성 중...
if not exist "D:\WSL" mkdir "D:\WSL"
if not exist "D:\WSL\Ubuntu-22.04" mkdir "D:\WSL\Ubuntu-22.04"

echo 6. Ubuntu 22.04 LTS를 D드라이브에 설치 중...
wsl --import Ubuntu-22.04 D:\WSL\Ubuntu-22.04 https://aka.ms/wslubuntu2204
if %errorlevel% neq 0 (
    echo Ubuntu 설치 실패!
    pause
    exit /b 1
)

echo 7. 기본 WSL 배포판 설정 중...
wsl --set-default Ubuntu-22.04
if %errorlevel% neq 0 (
    echo 기본 배포판 설정 실패!
    pause
    exit /b 1
)

echo 8. WSL 상태 확인 중...
wsl --list --verbose
echo.

echo ========================================
echo WSL D드라이브 설치 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. WSL에서 사용자 설정을 완료하세요
echo 2. Cursor를 설치하세요
echo 3. Docker Desktop을 설치하세요
echo 4. 프로젝트를 WSL로 복사하세요
echo.
echo Ubuntu 설치가 완료되면 Enter를 누르세요...
pause

echo 9. Cursor 설치 안내...
echo Cursor를 설치하려면 다음 URL로 이동하세요:
echo https://cursor.sh/
echo.
echo 설치 후 WSL 확장을 활성화하세요.
echo.

echo 10. Docker Desktop 설치 안내...
echo Docker Desktop을 설치하려면 다음 URL로 이동하세요:
echo https://www.docker.com/products/docker-desktop/
echo.
echo 설치 후 WSL2 백엔드를 활성화하세요.
echo.

echo ========================================
echo WSL D드라이브 설치 및 설정 완료!
echo ========================================
echo.
echo 이제 WSL에서 개발 환경을 설정할 수 있습니다.
echo.
pause 