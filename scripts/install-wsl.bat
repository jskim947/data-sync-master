@echo off
echo ========================================
echo WSL 설치 자동화 스크립트
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

echo 5. Ubuntu 22.04 LTS 설치 중...
wsl --install -d Ubuntu-22.04
if %errorlevel% neq 0 (
    echo Ubuntu 설치 실패!
    pause
    exit /b 1
)

echo.
echo ========================================
echo WSL 설치 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. Ubuntu가 설치되면 사용자명과 비밀번호를 설정하세요
echo 2. 프로젝트를 WSL로 복사하세요
echo 3. WSL에서 setup-wsl.sh 스크립트를 실행하세요
echo.
echo Ubuntu 설치가 완료되면 Enter를 누르세요...
pause

echo 6. WSL 상태 확인 중...
wsl --list --verbose
echo.
echo ========================================
echo WSL 설치 및 설정 완료!
echo ========================================
echo.
echo 이제 WSL에서 개발 환경을 설정할 수 있습니다.
echo.
pause 