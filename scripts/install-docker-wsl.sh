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

if [ $? -ne 0 ]; then
    log_error "필수 패키지 설치 실패"
    exit 1
fi

# 3. Docker GPG 키 추가
log_info "Docker GPG 키 추가 중..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

if [ $? -ne 0 ]; then
    log_error "Docker GPG 키 추가 실패"
    exit 1
fi

# 4. Docker 저장소 추가
log_info "Docker 저장소 추가 중..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Docker Engine 설치
log_info "Docker Engine 설치 중..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

if [ $? -ne 0 ]; then
    log_error "Docker Engine 설치 실패"
    exit 1
fi

# 6. Docker Compose 설치
log_info "Docker Compose 설치 중..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

if [ $? -ne 0 ]; then
    log_error "Docker Compose 설치 실패"
    exit 1
fi

# 7. Docker 서비스 설정
log_info "Docker 서비스 설정 중..."
sudo service docker start
sudo usermod -aG docker $USER

# 8. 설치 확인
log_info "Docker 설치 확인 중..."
docker --version
docker-compose --version

# 9. 테스트 컨테이너 실행
log_info "Docker 테스트 중..."
docker run --rm hello-world

if [ $? -eq 0 ]; then
    log_info "Docker 테스트 성공!"
else
    log_warn "Docker 테스트 실패 (권한 문제일 수 있음)"
fi

echo
echo "========================================"
echo "Docker 설치 완료!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. WSL을 재시작하거나 재로그인하세요"
echo "2. docker run hello-world로 테스트하세요"
echo "3. ./scripts/dev/start-dev.sh로 개발 환경을 시작하세요"
echo
echo "주의사항:"
echo "- Docker 그룹 권한을 적용하려면 재로그인이 필요합니다"
echo "- 권한 문제가 있으면: sudo usermod -aG docker \$USER"
echo "========================================" 