@echo off
echo ========================================
echo 클라이언트 SSH 키 생성
echo ========================================
echo.

echo 1. SSH 디렉토리 생성...
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

echo.
echo 2. SSH 키 생성...
ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\id_rsa" -N ""

echo.
echo 3. 공개키 내용 확인...
echo ========================================
echo 생성된 공개키 (서버에 등록해야 함):
echo ========================================
type "%USERPROFILE%\.ssh\id_rsa.pub"
echo ========================================
echo.
echo 4. 위의 공개키를 서버의 authorized_keys에 추가하세요.
echo.
echo 서버에서 실행할 명령어:
echo echo "위의_공개키_내용" ^>^> "%%USERPROFILE%%\.ssh\authorized_keys"
echo.
echo ========================================
echo SSH 키 생성 완료!
echo ======================================== 