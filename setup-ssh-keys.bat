@echo off
echo ========================================
echo SSH 키 설정 (클라이언트용)
echo ========================================
echo.

echo 1. SSH 디렉토리 생성...
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

echo.
echo 2. authorized_keys 파일 생성...
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2/tz26LfVGcosmlUhnTzmi/vrVFjykl6+PkaPPq3xxb0wePjlUjnXdv8Zl97NbPUcXnCOz7eEE/2NVGshnnuTrhkoh6xPSQKIRGxxINrFPCF8x1lx3bIQVUQb+dGNTQ51P6UFw4hQJhcVmLilOnomROEgr2+XyY750usnaGpGrPW0vIIuvuDf+qDkbxdDrLmBw0mibMUspOlLdmwAUwcDBbCbB/nfPvrPNcYymdaf+Ug9huEfKxqHLf+NKUkbM/d4NcrPKj9GHyCM0hmpM3VP2Z3OQHiW195Le1T/JW8+LWf1TZlfjN5xnN2C52fkR5sZ/B11uccIRNuSz+/mj+AtULm8eT3FM6jQitySks1jfeH/+Gk/00xflXCCr8zOR/KSS3AXKekRQfQnzrVtyHiCsxCnklLoZu66w+zhYYHuV68gCMR6ilTEpl7CQvto1wkWeNmuVZUGiVcNJohBBpd5Lk9Y2tljcJ3EPQZ3pmfZrBjv9e0hPyHSLjbXaZKmHOQpuIkNsEiZ6RPEJ1PhQ3rBonxxey+ZovfL+M3Rv84zBlVfkn45cwhnWKKwDQ5ZlM30RyS2W4cM/LHc9rJYnwQgzCHhNCUfJeIR+onJCndu01dCqv72DJIeI+8tKgBtcRS2uh0GCQNkfLgxOfkG4/yhN+pP+QFmbfQGJxsk6ya8fQ== data-sync-manager@local > "%USERPROFILE%\.ssh\authorized_keys"

echo.
echo 3. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh" /inheritance:r
icacls "%USERPROFILE%\.ssh" /grant:r "%USERNAME%:(F)"
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r
icacls "%USERPROFILE%\.ssh\authorized_keys" /grant:r "%USERNAME%:(F)"

echo.
echo 4. SSH 키 생성 (클라이언트용)...
ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\id_rsa" -N ""

echo.
echo ========================================
echo SSH 키 설정 완료!
echo ========================================
echo.
echo 생성된 파일:
echo - 개인키: %USERPROFILE%\.ssh\id_rsa
echo - 공개키: %USERPROFILE%\.ssh\id_rsa.pub
echo - 인증키: %USERPROFILE%\.ssh\authorized_keys
echo.
echo 공개키 내용 (서버에 등록해야 함):
echo ========================================
type "%USERPROFILE%\.ssh\id_rsa.pub"
echo ========================================
echo.
echo 서버에서 이 공개키를 authorized_keys에 추가하세요.
echo ======================================== 