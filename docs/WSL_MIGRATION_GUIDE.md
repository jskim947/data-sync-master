# 🐧 WSL 개발 환경 마이그레이션 가이드

## 🎯 WSL 마이그레이션 목적

### 1. 장점
- **Linux 환경**: 더 나은 개발 도구 지원
- **Docker 성능**: WSL2에서 Docker Desktop 성능 향상
- **패키지 관리**: apt, pip 등 Linux 패키지 매니저 활용
- **터미널**: 더 강력한 Linux 터미널 환경

### 2. 지원 환경
- **WSL2**: 권장 (Docker Desktop 지원)
- **Ubuntu 20.04/22.04**: 안정적인 LTS 버전
- **Windows 10/11**: 최신 버전 권장

## 📋 사전 준비사항

### 1. WSL 설치 확인
```powershell
# PowerShell에서 실행
wsl --list --verbose
```

### 2. WSL2 활성화
```powershell
# WSL2 활성화
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# WSL2 커널 업데이트
# https://aka.ms/wsl2kernel 에서 다운로드 후 설치
```

### 3. Ubuntu 설치
```powershell
# Microsoft Store에서 Ubuntu 22.04 LTS 설치
# 또는 명령어로 설치
wsl --install -d Ubuntu-22.04
```

## 🔄 프로젝트 마이그레이션 단계

### 1단계: WSL 환경 설정

#### Ubuntu 초기 설정
```bash
# WSL에서 실행
sudo apt update && sudo apt upgrade -y

# 필수 개발 도구 설치
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose
```

#### 사용자 설정
```bash
# Git 설정
git config --global user.name "jskim947"
git config --global user.email "kjs947@gmail.com"

# SSH 키 설정 (기존 키 복사)
cp /mnt/c/Users/infomax/.ssh/id_rsa ~/.ssh/
cp /mnt/c/Users/infomax/.ssh/id_rsa.pub ~/.ssh/
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### 2단계: 프로젝트 복사

#### Windows에서 WSL로 복사
```bash
# WSL 홈 디렉토리로 이동
cd ~

# Windows 프로젝트를 WSL로 복사
cp -r /mnt/d/data-sync-master/data-sync-master ./data-sync-master

# 프로젝트 디렉토리로 이동
cd data-sync-master
```

#### Git 저장소 재설정
```bash
# Git 상태 확인
git status

# 원격 저장소 연결 확인
git remote -v

# 필요시 원격 저장소 재설정
git remote set-url origin https://github.com/jskim947/data-sync-master.git
```

### 3단계: 개발 환경 설정

#### Python 가상환경 설정
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r src/requirements.txt
```

#### Docker 설정
```bash
# Docker 서비스 시작
sudo service docker start

# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER

# 변경사항 적용 (재로그인 필요)
newgrp docker
```

### 4단계: WSL 전용 스크립트 생성

#### Linux용 개발 스크립트
```bash
# scripts/dev/start-dev.sh 생성
cat > scripts/dev/start-dev.sh << 'EOF'
#!/bin/bash
echo "========================================"
echo "WSL 개발 환경 시작"
echo "========================================"
echo

echo "1. 기존 컨테이너 정리..."
docker-compose -f ../../docker/docker-compose.dev.yml down
echo

echo "2. 개발 환경 빌드 및 시작..."
docker-compose -f ../../docker/docker-compose.dev.yml up --build -d
echo

echo "3. 서비스 상태 확인..."
docker-compose -f ../../docker/docker-compose.dev.yml ps
echo

echo "4. 웹 애플리케이션 로그 확인..."
echo "로그를 확인하려면: docker-compose -f ../../docker/docker-compose.dev.yml logs -f web"
echo

echo "========================================"
echo "WSL 개발 환경 시작 완료!"
echo "========================================"
echo
echo "접속 정보:"
echo "- 웹 애플리케이션: http://localhost:5000"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
echo
echo "코드 수정 시 자동으로 반영됩니다."
echo "========================================"
EOF

# 실행 권한 부여
chmod +x scripts/dev/start-dev.sh
```

#### Linux용 자동 동기화 스크립트
```bash
# scripts/dev/auto-sync.sh 생성
cat > scripts/dev/auto-sync.sh << 'EOF'
#!/bin/bash
echo "========================================"
echo "Git 자동 동기화 시스템 (WSL)"
echo "========================================"
echo

echo "1. 개발 환경 시작..."
./scripts/dev/start-dev.sh
echo

echo "2. 자동 동기화 모니터링 시작..."
echo "클라이언트에서 Git 푸시하면 자동으로 반영됩니다."
echo

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git 변경사항 확인 중..."
    
    git fetch origin main
    if [ $? -ne 0 ]; then
        echo "Git fetch 실패, 재시도 중..."
        sleep 5
        continue
    fi
    
    if git status --porcelain | grep -q " M \| A \| D "; then
        echo "변경사항 감지! 업데이트 중..."
        git pull origin main
        docker-compose -f ../../docker/docker-compose.dev.yml restart web
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 업데이트 완료!"
    else
        echo "변경사항 없음"
    fi
    
    echo "5초 후 다시 확인..."
    sleep 5
done
EOF

# 실행 권한 부여
chmod +x scripts/dev/auto-sync.sh
```

### 5단계: VS Code WSL 확장 설정

#### VS Code에서 WSL 연결
1. **WSL 확장 설치**: VS Code에서 "WSL" 확장 설치
2. **WSL 연결**: `Ctrl+Shift+P` → "WSL: Connect to WSL"
3. **프로젝트 열기**: WSL 내 프로젝트 디렉토리 열기

#### VS Code 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "/home/username/data-sync-master/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/venv/**": true,
        "**/.git/**": true
    },
    "terminal.integrated.defaultProfile.linux": "bash"
}
```

## 🔧 WSL 전용 Docker 설정

### Docker Compose WSL 최적화
```yaml
# docker/docker-compose.wsl.yml
version: '3.8'
services:
  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:13
    container_name: data-sync-postgres-wsl
    environment:
      POSTGRES_DB: fs_master_web
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: infomax
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - wsl-network
    restart: unless-stopped

  # Redis 캐시
  redis:
    image: redis:6-alpine
    container_name: data-sync-redis-wsl
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - wsl-network
    restart: unless-stopped

  # 웹 애플리케이션 (WSL 최적화)
  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile.dev
    container_name: data-sync-web-wsl
    ports:
      - "5000:5000"
    volumes:
      # WSL 경로 최적화
      - ../src:/app/src
      - ../templates:/app/templates
      - ../tools:/app/tools
      - ../requirements.txt:/app/requirements.txt
    environment:
      - DATABASE_URL=postgresql://postgres:infomax@postgres:5432/fs_master_web
      - REDIS_URL=redis://redis:6379/0
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - PYTHONPATH=/app
    depends_on:
      - postgres
      - redis
    networks:
      - wsl-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  wsl-network:
    driver: bridge
```

## 🚀 WSL 개발 워크플로우

### 1. 일일 개발 시작
```bash
# WSL 터미널에서
cd ~/data-sync-master
source venv/bin/activate
./scripts/dev/start-dev.sh
```

### 2. 코드 수정 및 테스트
```bash
# VS Code에서 WSL 연결 후 개발
# 코드 수정 시 자동으로 Docker에 반영
```

### 3. Git 동기화
```bash
# 변경사항 커밋
git add .
git commit -m "WSL 환경에서 개발 완료"
git push origin main
```

### 4. 자동 동기화 모니터링
```bash
# 별도 터미널에서 실행
./scripts/dev/auto-sync.sh
```

## 🔍 문제 해결

### 1. WSL 성능 최적화
```bash
# WSL 설정 파일 생성
cat > ~/.wslconfig << EOF
[wsl2]
memory=4GB
processors=4
swap=2GB
localhostForwarding=true
EOF
```

### 2. Docker 권한 문제
```bash
# Docker 그룹 권한 확인
groups $USER

# Docker 서비스 상태 확인
sudo service docker status

# 필요시 Docker 재시작
sudo service docker restart
```

### 3. 네트워크 연결 문제
```bash
# WSL 네트워크 상태 확인
ip addr show

# Windows 호스트 연결 확인
ping $(hostname).local
```

## 📊 WSL vs Windows 비교

| 항목 | Windows | WSL |
|------|---------|-----|
| **Docker 성능** | 보통 | 우수 |
| **터미널** | PowerShell | Bash/Zsh |
| **패키지 관리** | Chocolatey | apt/pip |
| **개발 도구** | 제한적 | 풍부 |
| **파일 시스템** | NTFS | ext4 |
| **메모리 사용** | 높음 | 낮음 |

## ✅ 마이그레이션 체크리스트

### WSL 환경 설정
- [ ] WSL2 설치 및 활성화
- [ ] Ubuntu 22.04 설치
- [ ] 기본 개발 도구 설치
- [ ] Git 설정 완료
- [ ] SSH 키 복사 및 권한 설정

### 프로젝트 마이그레이션
- [ ] 프로젝트 파일 복사
- [ ] Git 저장소 재설정
- [ ] Python 가상환경 설정
- [ ] 의존성 설치 완료
- [ ] Docker 환경 설정

### 개발 도구 설정
- [ ] VS Code WSL 확장 설치
- [ ] WSL 전용 스크립트 생성
- [ ] Docker Compose WSL 최적화
- [ ] 자동 동기화 스크립트 설정
- [ ] 개발 환경 테스트 완료

## 🎉 마이그레이션 완료 후

### 성능 향상 확인
- Docker 컨테이너 시작 속도 개선
- 파일 I/O 성능 향상
- 메모리 사용량 최적화

### 개발 효율성 향상
- Linux 명령어 활용
- 강력한 터미널 환경
- 풍부한 개발 도구

**WSL 환경으로 마이그레이션하면 더욱 효율적인 개발 환경을 구축할 수 있습니다!** 🚀 