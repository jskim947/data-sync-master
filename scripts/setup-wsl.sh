#!/bin/bash
echo "========================================"
echo "WSL 개발 환경 자동 설정"
echo "========================================"
echo

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 시스템 업데이트
log_info "시스템 패키지 업데이트 중..."
sudo apt update && sudo apt upgrade -y
if [ $? -eq 0 ]; then
    log_info "시스템 업데이트 완료"
else
    log_error "시스템 업데이트 실패"
    exit 1
fi

# 2. 필수 개발 도구 설치
log_info "개발 도구 설치 중..."
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv

if [ $? -eq 0 ]; then
    log_info "개발 도구 설치 완료"
else
    log_error "개발 도구 설치 실패"
    exit 1
fi

# 3. Git 설정
log_info "Git 설정 중..."
git config --global user.name "jskim947"
git config --global user.email "kjs947@gmail.com"
log_info "Git 설정 완료"

# 4. SSH 키 복사 (Windows에서)
log_info "SSH 키 복사 중..."
if [ -d "/mnt/c/Users/infomax/.ssh" ]; then
    mkdir -p ~/.ssh
    cp /mnt/c/Users/infomax/.ssh/id_rsa ~/.ssh/ 2>/dev/null || log_warn "SSH 개인키 복사 실패 (없을 수 있음)"
    cp /mnt/c/Users/infomax/.ssh/id_rsa.pub ~/.ssh/ 2>/dev/null || log_warn "SSH 공개키 복사 실패 (없을 수 있음)"
    
    if [ -f ~/.ssh/id_rsa ]; then
        chmod 600 ~/.ssh/id_rsa
        log_info "SSH 키 권한 설정 완료"
    fi
    if [ -f ~/.ssh/id_rsa.pub ]; then
        chmod 644 ~/.ssh/id_rsa.pub
    fi
else
    log_warn "Windows SSH 키 디렉토리를 찾을 수 없습니다"
fi

# 5. Docker Engine 설치
log_info "Docker Engine 설치 중..."
if [ -f "scripts/install-docker-wsl.sh" ]; then
    chmod +x scripts/install-docker-wsl.sh
    ./scripts/install-docker-wsl.sh
else
    log_warn "Docker 설치 스크립트를 찾을 수 없습니다"
    log_info "수동으로 Docker를 설치하세요: ./scripts/install-docker-wsl.sh"
fi

# 6. Python 가상환경 설정
log_info "Python 가상환경 설정 중..."
if [ -f "src/requirements.txt" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt
    log_info "Python 가상환경 설정 완료"
else
    log_warn "requirements.txt 파일을 찾을 수 없습니다"
fi

# 7. 스크립트 실행 권한 설정
log_info "스크립트 실행 권한 설정 중..."
chmod +x scripts/dev/*.sh
chmod +x scripts/setup-wsl.sh
log_info "스크립트 권한 설정 완료"

# 8. WSL 설정 파일 생성
log_info "WSL 성능 최적화 설정 중..."
cat > ~/.wslconfig << EOF
[wsl2]
memory=4GB
processors=4
swap=2GB
localhostForwarding=true
EOF
log_info "WSL 설정 파일 생성 완료"

echo
echo "========================================"
echo "WSL 개발 환경 설정 완료!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. WSL을 재시작하세요: wsl --shutdown"
echo "2. VS Code에서 WSL 확장을 설치하세요"
echo "3. 개발 환경을 시작하세요: ./scripts/dev/start-dev.sh"
echo
echo "주의사항:"
echo "- Docker 그룹 권한을 적용하려면 재로그인이 필요합니다"
echo "- WSL 설정 변경사항을 적용하려면 WSL을 재시작해야 합니다"
echo "========================================" 