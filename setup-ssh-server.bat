@echo off
echo ========================================
echo Windows SSH 서버 설정
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
echo ========================================
echo SSH 서버 설정 완료!
echo ========================================
echo.
echo 접속 정보:
echo - IP 주소: 172.27.64.1
echo - 포트: 22
echo - 사용자: 현재 Windows 사용자명
echo - 비밀번호: Windows 계정 비밀번호
echo.
echo VS Code Remote-SSH 설정:
echo Host: 172.27.64.1
echo Port: 22
echo Username: 현재 Windows 사용자명
echo.
echo 명령어:
echo - SSH 서비스 상태 확인: sc query sshd
echo - SSH 서비스 시작: net start sshd
echo - SSH 서비스 중지: net stop sshd
echo ======================================== 