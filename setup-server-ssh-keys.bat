@echo off
echo ========================================
echo 서버 SSH 키 설정
echo ========================================
echo.

echo 1. SSH 디렉토리 생성...
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

echo.
echo 2. authorized_keys 파일에 클라이언트 공개키 추가...
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2/tz26LfVGcosmlUhnTzmi/vrVFjykl6+PkaPPq3xxb0wePjlUjnXdv8Zl97NbPUcXnCOz7eEE/2NVGshnnuTrhkoh6xPSQKIRGxxINrFPCF8x1lx3bIQVUQb+dGNTQ51P6UFw4hQJhcVmLilOnomROEgr2+XyY750usnaGpGrPW0vIIuvuDf+qDkbxdDrLmBw0mibMUspOlLdmwAUwcDBbCbB/nfPvrPNcYymdaf+Ug9huEfKxqHLf+NKUkbM/d4NcrPKj9GHyCM0hmpM3VP2Z3OQHiW195Le1T/JW8+LWf1TZlfjN5xnN2C52fkR5sZ/B11uccIRNuSz+/mj+AtULm8eT3FM6jQitySks1jfeH/+Gk/00xflXCCr8zOR/KSS3AXKekRQfQnzrVtyHiCsxCnklLoZu66w+zhYYHuV68gCMR6ilTEpl7CQvto1wkWeNmuVZUGiVcNJohBBpd5Lk9Y2tljcJ3EPQZ3pmfZrBjv9e0hPyHSLjbXaZKmHOQpuIkNsEiZ6RPEJ1PhQ3rBonxxey+ZovfL+M3Rv84zBlVfkn45cwhnWKKwDQ5ZlM30RyS2W4cM/LHc9rJYnwQgzCHhNCUfJeIR+onJCndu01dCqv72DJIeI+8tKgBtcRS2uh0GCQNkfLgxOfkG4/yhN+pP+QFmbfQGJxsk6ya8fQ== data-sync-manager@local >> "%USERPROFILE%\.ssh\authorized_keys"

echo.
echo 3. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh" /inheritance:r
icacls "%USERPROFILE%\.ssh" /grant:r "%USERNAME%:(F)"
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r
icacls "%USERPROFILE%\.ssh\authorized_keys" /grant:r "%USERNAME%:(F)"

echo.
echo 4. SSH 서버 설정 확인...
echo SSH 서버가 실행 중인지 확인합니다.
sc query sshd

echo.
echo ========================================
echo 서버 SSH 키 설정 완료!
echo ========================================
echo.
echo 설정된 내용:
echo - SSH 디렉토리: %USERPROFILE%\.ssh
echo - 인증키 파일: %USERPROFILE%\.ssh\authorized_keys
echo.
echo 클라이언트에서 다음으로 접속 가능:
echo ssh %USERNAME%@172.27.64.1
echo.
echo VS Code Remote-SSH 설정:
echo Host: 172.27.64.1
echo User: %USERNAME%
echo ======================================== 