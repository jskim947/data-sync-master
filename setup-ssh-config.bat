@echo off
echo ========================================
echo SSH 키 기본 사용 설정
echo ========================================
echo.

echo 1. SSH 디렉토리 생성...
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

echo.
echo 2. SSH 설정 파일 생성...
echo Host 10.150.2.150 > "%USERPROFILE%\.ssh\config"
echo     HostName 10.150.2.150 >> "%USERPROFILE%\.ssh\config"
echo     User infomax >> "%USERPROFILE%\.ssh\config"
echo     Port 22 >> "%USERPROFILE%\.ssh\config"
echo     IdentityFile ~/.ssh/id_rsa_data_sync >> "%USERPROFILE%\.ssh\config"
echo     PreferredAuthentications publickey >> "%USERPROFILE%\.ssh\config"
echo     PubkeyAuthentication yes >> "%USERPROFILE%\.ssh\config"
echo     PasswordAuthentication no >> "%USERPROFILE%\.ssh\config"
echo     IdentitiesOnly yes >> "%USERPROFILE%\.ssh\config"
echo     StrictHostKeyChecking no >> "%USERPROFILE%\.ssh\config"
echo     UserKnownHostsFile /dev/null >> "%USERPROFILE%\.ssh\config"

echo.
echo 3. 전역 SSH 설정 (모든 호스트에 적용)...
echo Host * >> "%USERPROFILE%\.ssh\config"
echo     PreferredAuthentications publickey >> "%USERPROFILE%\.ssh\config"
echo     PubkeyAuthentication yes >> "%USERPROFILE%\.ssh\config"
echo     PasswordAuthentication no >> "%USERPROFILE%\.ssh\config"
echo     IdentitiesOnly yes >> "%USERPROFILE%\.ssh\config"

echo.
echo 4. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh\config" /inheritance:r
icacls "%USERPROFILE%\.ssh\config" /grant:r "%USERNAME%:(F)"

echo.
echo 5. 설정 확인...
echo ========================================
echo SSH 설정 파일 내용:
echo ========================================
type "%USERPROFILE%\.ssh\config"
echo ========================================
echo.
echo ========================================
echo SSH 키 기본 사용 설정 완료!
echo ========================================
echo.
echo 이제 SSH는 자동으로 키 인증을 사용합니다.
echo 테스트: ssh 10.150.2.150
echo 또는: ssh infomax@10.150.2.150
echo.
echo VS Code Remote-SSH 설정:
echo Host: 10.150.2.150
echo User: infomax
echo ======================================== 