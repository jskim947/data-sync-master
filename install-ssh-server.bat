@echo off
echo ========================================
echo Windows SSH 서버 실제 설치 및 설정
echo ========================================
echo.
echo 이 스크립트는 관리자 권한으로 실행해야 합니다.
echo.

echo 1. OpenSSH 서버 기능 설치...
dism /online /add-capability /capabilityname:OpenSSH.Server~~~~0.0.1.0

echo.
echo 2. SSH 서버 서비스 시작...
net start sshd

echo.
echo 3. SSH 서버 자동 시작 설정...
sc config sshd start=auto

echo.
echo 4. 방화벽 규칙 추가...
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=TCP localport=22

echo.
echo 5. SSH 디렉토리 생성...
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

echo.
echo 6. authorized_keys 파일 생성...
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2/tz26LfVGcosmlUhnTzmi/vrVFjykl6+PkaPPq3xxb0wePjlUjnXdv8Zl97NbPUcXnCOz7eEE/2NVGshnnuTrhkoh6xPSQKIRGxxINrFPCF8x1lx3bIQVUQb+dGNTQ51P6UFw4hQJhcVmLilOnomROEgr2+XyY750usnaGpGrPW0vIIuvuDf+qDkbxdDrLmBw0mibMUspOlLdmwAUwcDBbCbB/nfPvrPNcYymdaf+Ug9huEfKxqHLf+NKUkbM/d4NcrPKj9GHyCM0hmpM3VP2Z3OQHiW195Le1T/JW8+LWf1TZlfjN5xnN2C52fkR5sZ/B11uccIRNuSz+/mj+AtULm8eT3FM6jQitySks1jfeH/+Gk/00xflXCCr8zOR/KSS3AXKekRQfQnzrVtyHiCsxCnklLoZu66w+zhYYHuV68gCMR6ilTEpl7CQvto1wkWeNmuVZUGiVcNJohBBpd5Lk9Y2tljcJ3EPQZ3pmfZrBjv9e0hPyHSLjbXaZKmHOQpuIkNsEiZ6RPEJ1PhQ3rBonxxey+ZovfL+M3Rv84zBlVfkn45cwhnWKKwDQ5ZlM30RyS2W4cM/LHc9rJYnwQgzCHhNCUfJeIR+onJCndu01dCqv72DJIeI+8tKgBtcRS2uh0GCQNkfLgxOfkG4/yhN+pP+QFmbfQGJxsk6ya8fQ== data-sync-manager@local > "%USERPROFILE%\.ssh\authorized_keys"

echo.
echo 7. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh" /inheritance:r
icacls "%USERPROFILE%\.ssh" /grant:r "%USERNAME%:(F)"
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r
icacls "%USERPROFILE%\.ssh\authorized_keys" /grant:r "%USERNAME%:(F)"

echo.
echo 8. SSH 서버 설정 확인...
sc query sshd

echo.
echo 9. IP 주소 확인...
ipconfig | findstr "IPv4"

echo.
echo ========================================
echo SSH 서버 설치 및 설정 완료!
echo ========================================
echo.
echo 접속 정보:
echo - IP 주소: 위에서 확인된 IP
echo - 포트: 22
echo - 사용자: %USERNAME%
echo - 비밀번호: Windows 계정 비밀번호
echo.
echo 테스트 명령어:
echo ssh %USERNAME%@IP주소
echo.
echo VS Code Remote-SSH 설정:
echo Host: IP주소
echo User: %USERNAME%
echo ======================================== 