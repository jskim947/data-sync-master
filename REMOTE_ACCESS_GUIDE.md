# 🔗 원격 접속 설정 가이드

이 컴퓨터(172.27.64.1)에 다른 컴퓨터에서 접속하여 개발할 수 있도록 설정하는 방법입니다.

## 🚀 방법 1: Windows SSH 서버 설정 (권장)

### 1단계: 관리자 권한으로 SSH 서버 설치

**관리자 권한으로 PowerShell을 실행**하고 다음 명령어를 실행하세요:

```powershell
# OpenSSH 서버 기능 설치
dism /online /add-capability /capabilityname:OpenSSH.Server~~~~0.0.1.0

# SSH 서버 서비스 시작
net start sshd

# SSH 서버 자동 시작 설정
sc config sshd start=auto

# 방화벽 규칙 추가
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=TCP localport=22
```

또는 `setup-ssh-server.bat` 파일을 **관리자 권한으로 실행**하세요.

### 2단계: 접속 정보 확인

- **IP 주소**: `172.27.64.1`
- **포트**: `22`
- **사용자명**: 현재 Windows 사용자명
- **비밀번호**: Windows 계정 비밀번호

## 💻 방법 2: VS Code Remote-SSH 사용 (가장 편리)

### 1단계: VS Code에서 Remote-SSH 확장 설치

1. VS Code 열기
2. `Ctrl+Shift+X`로 확장 마켓플레이스 열기
3. "Remote - SSH" 검색 후 설치

### 2단계: 원격 서버 연결

1. `Ctrl+Shift+P`로 명령 팔레트 열기
2. "Remote-SSH: Connect to Host" 선택
3. `사용자명@172.27.64.1` 입력
4. 비밀번호 입력

### 3단계: 원격 개발

- 원격 서버의 파일을 로컬처럼 편집
- 터미널에서 원격 명령 실행
- 디버깅 및 확장 기능 사용 가능

## 🖥️ 방법 3: 터미널 SSH 접속

### Linux/Mac에서:
```bash
ssh 사용자명@172.27.64.1
```

### Windows에서:
```bash
# PowerShell 또는 Git Bash에서
ssh 사용자명@172.27.64.1
```

## 🔧 개발 환경 설정

### 1단계: 원격 서버에서 개발 환경 시작

SSH로 접속한 후:

```bash
# 프로젝트 디렉토리로 이동
cd /d/data-sync-master/data-sync-master

# Docker 개발 환경 시작
docker-compose -f docker-compose.remote-dev.yml up --build -d
```

### 2단계: 접속 확인

- **웹 애플리케이션**: `http://172.27.64.1:5000`
- **PostgreSQL**: `172.27.64.1:5432`
- **Redis**: `172.27.64.1:6379`

## 📋 권장 워크플로우

### 로컬에서 수정하는 경우:
1. VS Code Remote-SSH로 연결
2. 원격 파일을 로컬처럼 편집
3. 저장 시 즉시 반영 (Flask 개발 모드)

### Git을 통한 배포:
1. 로컬에서 코드 수정
2. Git 커밋 및 푸시
3. 원격 서버에서 `git pull` 후 재시작

## 🛠️ 문제 해결

### SSH 연결이 안 될 때:
1. **방화벽 확인**: Windows 방화벽에서 포트 22 허용
2. **서비스 상태 확인**: `sc query sshd`
3. **네트워크 연결 확인**: `ping 172.27.64.1`

### 권한 문제:
1. **관리자 권한으로 실행**: SSH 서버 설치 시 필요
2. **사용자 계정 확인**: Windows 계정 정보 확인

### 포트 충돌:
1. **포트 사용 확인**: `netstat -an | findstr :22`
2. **다른 포트 사용**: SSH 설정에서 포트 변경

## 📞 지원

문제가 발생하면:
1. SSH 서비스 로그 확인: 이벤트 뷰어
2. 네트워크 연결 테스트: `telnet 172.27.64.1 22`
3. Docker 상태 확인: `docker ps`

## 🔒 보안 주의사항

1. **강력한 비밀번호 사용**
2. **SSH 키 인증 사용 권장**
3. **방화벽 설정 확인**
4. **정기적인 보안 업데이트** 