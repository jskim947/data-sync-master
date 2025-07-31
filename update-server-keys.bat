@echo off
echo ========================================
echo 서버 SSH 키 업데이트
echo ========================================
echo.

echo 1. 기존 authorized_keys 파일 백업...
if exist "%USERPROFILE%\.ssh\authorized_keys" (
    copy "%USERPROFILE%\.ssh\authorized_keys" "%USERPROFILE%\.ssh\authorized_keys.backup"
    echo 백업 완료: authorized_keys.backup
)

echo.
echo 2. 새로운 authorized_keys 파일 생성...
echo 클라이언트에서 생성한 공개키를 입력하세요.
echo (ssh-rsa로 시작하는 긴 문자열)
echo.
set /p PUBLIC_KEY="공개키를 입력하세요: "

echo %PUBLIC_KEY% > "%USERPROFILE%\.ssh\authorized_keys"

echo.
echo 3. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r
icacls "%USERPROFILE%\.ssh\authorized_keys" /grant:r "%USERNAME%:(F)"

echo.
echo 4. 설정 확인...
echo ========================================
echo 현재 authorized_keys 내용:
echo ========================================
type "%USERPROFILE%\.ssh\authorized_keys"
echo ========================================
echo.
echo ========================================
echo SSH 키 업데이트 완료!
echo ========================================
echo.
echo 이제 클라이언트에서 SSH 키로 접속할 수 있습니다.
echo 테스트: ssh %USERNAME%@10.150.2.150
echo ======================================== 