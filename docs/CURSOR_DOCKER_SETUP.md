# 🖥️ Cursor & Docker Desktop WSL 설정 가이드

## 🎯 설치 목표

### 1. Cursor 설치
- **AI 기반 코드 에디터**: GitHub Copilot 통합
- **WSL 확장**: WSL 환경에서 직접 개발
- **원격 개발**: WSL 내 프로젝트 편집

### 2. Docker Desktop 설치
- **WSL2 백엔드**: WSL2 기반 Docker 실행
- **GUI 관리**: 컨테이너 및 이미지 관리
- **자동 동기화**: WSL과 Windows 간 연동

## 📋 Cursor 설치 및 설정

### 1단계: Cursor 다운로드 및 설치
```powershell
# Windows에서 실행
# https://cursor.sh/ 에서 다운로드
# 또는 winget 사용
winget install Cursor.Cursor
```

### 2단계: Cursor WSL 확장 설정
1. **Cursor 실행**
2. **확장 설치**: `Ctrl+Shift+X`
3. **WSL 확장 검색**: "WSL" 또는 "Remote - WSL"
4. **설치**: "Remote - WSL" 확장 설치

### 3단계: WSL 연결
1. **WSL 연결**: `Ctrl+Shift+P` → "WSL: Connect to WSL"
2. **배포판 선택**: Ubuntu-22.04 선택
3. **프로젝트 열기**: WSL 내 프로젝트 디렉토리 열기

### 4단계: Cursor 설정 최적화
```json
// .vscode/settings.json (WSL 내)
{
    "python.defaultInterpreterPath": "/home/username/projects/data-sync-master/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/venv/**": true,
        "**/.git/**": true
    },
    "terminal.integrated.defaultProfile.linux": "bash",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

## 🐳 Docker Desktop 설치 및 설정

### 1단계: Docker Desktop 다운로드
```powershell
# Windows에서 실행
# https://www.docker.com/products/docker-desktop 에서 다운로드
# 또는 winget 사용
winget install Docker.DockerDesktop
```

### 2단계: WSL2 백엔드 활성화
1. **Docker Desktop 실행**
2. **Settings 열기**: 우상단 설정 아이콘 클릭
3. **General 탭**: "Use the WSL 2 based engine" 체크
4. **Resources 탭**: WSL Integration 선택
5. **WSL Integration 설정**:
   - "Enable integration with my default WSL distro" 체크
   - "Ubuntu-22.04" 체크
6. **Apply & Restart**: 변경사항 적용 및 재시작

### 3단계: WSL에서 Docker 확인
```bash
# WSL에서 실행
docker --version
docker-compose --version
docker run hello-world
```

### 4단계: Docker 권한 설정
```bash
# WSL에서 실행 (필요시)
sudo usermod -aG docker $USER
newgrp docker
```

## 🔧 통합 설정

### 1. Cursor에서 Docker 연동
```json
// .vscode/settings.json (WSL 내)
{
    "docker.host": "unix:///var/run/docker.sock",
    "docker.context": "default",
    "docker.composePath": "docker-compose",
    "docker.command": "docker"
}
```

### 2. 프로젝트별 설정
```json
// .vscode/launch.json (WSL 내)
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/app.py",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": ["--host=0.0.0.0", "--port=5000"],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### 3. 터미널 설정
```json
// .vscode/settings.json (WSL 내)
{
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "bash",
            "icon": "terminal-bash"
        }
    },
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}/src"
    }
}
```

## 🚀 개발 워크플로우

### 1. Cursor에서 WSL 프로젝트 열기
```bash
# WSL에서 실행
cd ~/projects/data-sync-master
code .
```

### 2. Docker 컨테이너 관리
```bash
# Cursor 터미널에서 실행
# 개발 환경 시작
./scripts/dev/start-dev.sh

# 컨테이너 상태 확인
docker-compose -f docker/docker-compose.wsl.yml ps

# 로그 확인
docker-compose -f docker/docker-compose.wsl.yml logs -f web
```

### 3. 코드 수정 및 테스트
- **실시간 반영**: 볼륨 마운트로 코드 수정 시 자동 반영
- **디버깅**: Cursor 디버거로 Python 코드 디버깅
- **Git 관리**: Cursor Git 패널로 버전 관리

## 📊 성능 최적화

### 1. WSL 메모리 설정
```bash
# Windows에서 ~/.wslconfig 파일 생성
cat > ~/.wslconfig << EOF
[wsl2]
memory=6GB
processors=4
swap=2GB
localhostForwarding=true
EOF

# WSL 재시작
wsl --shutdown
```

### 2. Docker Desktop 리소스 설정
1. **Docker Desktop Settings**
2. **Resources 탭**
3. **Memory**: 4GB 이상 할당
4. **CPUs**: 2개 이상 할당
5. **Disk image size**: 64GB 이상

### 3. 파일 시스템 최적화
```bash
# WSL에서 실행
# 프로젝트를 WSL 파일시스템에 저장 (Windows 드라이브 마운트 대신)
# /home/username/projects/ 에 프로젝트 저장
```

## 🔍 문제 해결

### 1. Cursor WSL 연결 문제
```bash
# WSL 상태 확인
wsl --list --verbose

# WSL 재시작
wsl --shutdown
wsl

# Cursor 재시작
```

### 2. Docker 권한 문제
```bash
# Docker 그룹 확인
groups $USER

# Docker 그룹에 추가
sudo usermod -aG docker $USER

# 재로그인
exit
# 다시 WSL 접속
```

### 3. 네트워크 연결 문제
```bash
# WSL 네트워크 확인
ip addr show

# Docker 네트워크 확인
docker network ls

# 포트 확인
netstat -tulpn | grep :5000
```

## ✅ 설치 확인 체크리스트

### Cursor 설정
- [ ] Cursor 설치 완료
- [ ] WSL 확장 설치 완료
- [ ] WSL 연결 성공
- [ ] 프로젝트 열기 성공
- [ ] Python 인터프리터 설정 완료

### Docker Desktop 설정
- [ ] Docker Desktop 설치 완료
- [ ] WSL2 백엔드 활성화
- [ ] WSL Integration 활성화
- [ ] Docker 명령어 실행 성공
- [ ] 컨테이너 실행 테스트 성공

### 통합 테스트
- [ ] Cursor에서 Docker 명령어 실행
- [ ] 프로젝트 컨테이너 시작
- [ ] 코드 수정 시 자동 반영
- [ ] 디버깅 기능 정상 작동
- [ ] Git 연동 정상 작동

## 🎯 최종 권장사항

### 개발 환경 구성
1. **WSL2**: Ubuntu 22.04 LTS
2. **Cursor**: AI 기반 코드 에디터
3. **Docker Desktop**: WSL2 백엔드
4. **Python**: 가상환경 사용

### 워크플로우
1. **Cursor에서 WSL 프로젝트 열기**
2. **Docker 컨테이너 시작**
3. **코드 수정 및 테스트**
4. **Git으로 버전 관리**

**Cursor와 Docker Desktop을 WSL과 연동하면 최고의 개발 환경을 구축할 수 있습니다!** 🚀 