# 🐳 WSL Docker 설치 및 설정 가이드

## 🎯 WSL Docker 설치 옵션

### 옵션 1: WSL 내 Docker Engine 설치 (권장)
- **장점**: 더 빠른 성능, 더 많은 제어권
- **단점**: 별도 설정 필요

### 옵션 2: Docker Desktop WSL2 백엔드 사용
- **장점**: 간편한 설정, GUI 관리
- **단점**: 리소스 사용량 증가

## 📋 WSL 내 Docker Engine 설치

### 1단계: 기존 Docker 제거 (있다면)
```bash
# WSL에서 실행
sudo apt remove docker docker-engine docker.io containerd runc
sudo apt autoremove
```

### 2단계: Docker 저장소 설정
```bash
# 필수 패키지 설치
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker 공식 GPG 키 추가
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker 저장소 추가
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 3단계: Docker Engine 설치
```bash
# 패키지 목록 업데이트
sudo apt update

# Docker Engine 설치
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker Compose 설치 (별도)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4단계: Docker 서비스 설정
```bash
# Docker 서비스 시작
sudo service docker start

# 부팅 시 자동 시작 설정
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 변경사항 적용 (재로그인 필요)
newgrp docker
```

### 5단계: Docker 설치 확인
```bash
# Docker 버전 확인
docker --version
docker-compose --version

# Docker 서비스 상태 확인
sudo service docker status

# 테스트 컨테이너 실행
docker run hello-world
```

## 🔧 Docker Desktop WSL2 백엔드 설정

### 1단계: Docker Desktop 설치
```powershell
# Windows에서 실행
# https://www.docker.com/products/docker-desktop 에서 다운로드
```

### 2단계: WSL2 백엔드 활성화
1. Docker Desktop 실행
2. Settings → General → "Use the WSL 2 based engine" 체크
3. Settings → Resources → WSL Integration
4. "Enable integration with my default WSL distro" 체크
5. "Ubuntu-22.04" 체크
6. Apply & Restart

### 3단계: WSL에서 Docker 확인
```bash
# WSL에서 실행
docker --version
docker-compose --version
docker run hello-world
```

## 📊 두 방법 비교

| 항목 | WSL 내 Docker Engine | Docker Desktop WSL2 |
|------|---------------------|---------------------|
| **설치 복잡도** | ⭐⭐⭐ | ⭐ |
| **성능** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **리소스 사용** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **제어권** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **GUI 관리** | ❌ | ✅ |
| **자동 업데이트** | ❌ | ✅ |

## 🚀 권장 설정: WSL 내 Docker Engine

### 자동 설치 스크립트
```bash
# scripts/install-docker-wsl.sh 생성
cat > scripts/install-docker-wsl.sh << 'EOF'
#!/bin/bash
echo "========================================"
echo "WSL Docker Engine 설치"
echo "========================================"
echo

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 기존 Docker 제거
log_info "기존 Docker 제거 중..."
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null
sudo apt autoremove -y

# 2. 필수 패키지 설치
log_info "필수 패키지 설치 중..."
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Docker GPG 키 추가
log_info "Docker GPG 키 추가 중..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. Docker 저장소 추가
log_info "Docker 저장소 추가 중..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Docker Engine 설치
log_info "Docker Engine 설치 중..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. Docker Compose 설치
log_info "Docker Compose 설치 중..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 7. Docker 서비스 설정
log_info "Docker 서비스 설정 중..."
sudo service docker start
sudo usermod -aG docker $USER

# 8. 설치 확인
log_info "Docker 설치 확인 중..."
docker --version
docker-compose --version

echo
echo "========================================"
echo "Docker 설치 완료!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. WSL을 재시작하거나 재로그인하세요"
echo "2. docker run hello-world로 테스트하세요"
echo "3. ./scripts/dev/start-dev.sh로 개발 환경을 시작하세요"
echo "========================================"
EOF

chmod +x scripts/install-docker-wsl.sh
```

## 🔍 문제 해결

### 1. Docker 권한 문제
```bash
# Docker 그룹 확인
groups $USER

# Docker 그룹에 추가
sudo usermod -aG docker $USER

# 재로그인 또는 그룹 변경사항 적용
newgrp docker
```

### 2. Docker 서비스 시작 실패
```bash
# Docker 서비스 상태 확인
sudo service docker status

# Docker 서비스 재시작
sudo service docker restart

# Docker 데몬 로그 확인
sudo journalctl -u docker.service
```

### 3. WSL2 메모리 부족
```bash
# WSL 설정 파일 수정
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

## ✅ 설치 확인 체크리스트

### 기본 설치
- [ ] Docker Engine 설치 완료
- [ ] Docker Compose 설치 완료
- [ ] Docker 서비스 시작됨
- [ ] 사용자가 docker 그룹에 추가됨

### 기능 테스트
- [ ] `docker --version` 실행됨
- [ ] `docker-compose --version` 실행됨
- [ ] `docker run hello-world` 성공
- [ ] 프로젝트 Docker Compose 실행됨

### 성능 확인
- [ ] 컨테이너 시작 시간 < 10초
- [ ] 볼륨 마운트 정상 작동
- [ ] 네트워크 연결 정상
- [ ] 파일 동기화 정상

## 🎯 최종 권장사항

### 개발 환경용: WSL 내 Docker Engine
```bash
# WSL에서 실행
./scripts/install-docker-wsl.sh
```

### 프로덕션 환경용: Docker Desktop WSL2
- GUI 관리가 필요한 경우
- 팀 협업 환경에서 일관성 유지가 중요한 경우

**WSL 내 Docker Engine이 개발 환경에 가장 적합합니다!** 🚀 