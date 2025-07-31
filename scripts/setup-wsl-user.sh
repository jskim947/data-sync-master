#!/bin/bash
echo "========================================"
echo "WSL 사용자 설정 및 개발 환경 구성"
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

# 1. 사용자 설정 확인
log_info "사용자 설정 확인 중..."
if [ "$(whoami)" = "root" ]; then
    log_warn "root 사용자로 실행 중입니다. 일반 사용자로 전환하세요."
    echo "사용자명을 입력하세요 (예: wsluser):"
    read username
    echo "비밀번호를 입력하세요:"
    read -s password
    echo "비밀번호를 다시 입력하세요:"
    read -s password2
    
    if [ "$password" != "$password2" ]; then
        log_error "비밀번호가 일치하지 않습니다."
        exit 1
    fi
    
    # 사용자 생성
    useradd -m -s /bin/bash $username
    echo "$username:$password" | chpasswd
    usermod -aG sudo $username
    
    log_info "사용자 $username 생성 완료"
    log_info "다음 명령어로 사용자를 전환하세요:"
    echo "su - $username"
    echo "그 후 이 스크립트를 다시 실행하세요."
    exit 0
fi

# 2. 시스템 업데이트
log_info "시스템 패키지 업데이트 중..."
sudo apt update && sudo apt upgrade -y
if [ $? -eq 0 ]; then
    log_info "시스템 업데이트 완료"
else
    log_error "시스템 업데이트 실패"
    exit 1
fi

# 3. 필수 개발 도구 설치
log_info "개발 도구 설치 중..."
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    vim \
    htop \
    tree

if [ $? -eq 0 ]; then
    log_info "개발 도구 설치 완료"
else
    log_error "개발 도구 설치 실패"
    exit 1
fi

# 4. Git 설정
log_info "Git 설정 중..."
git config --global user.name "jskim947"
git config --global user.email "kjs947@gmail.com"
log_info "Git 설정 완료"

# 5. SSH 키 복사 (Windows에서)
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

# 6. 프로젝트 디렉토리 설정
log_info "프로젝트 디렉토리 설정 중..."
mkdir -p ~/projects
cd ~/projects

# Windows 프로젝트를 WSL로 복사
if [ -d "/mnt/d/data-sync-master/data-sync-master" ]; then
    cp -r /mnt/d/data-sync-master/data-sync-master ./data-sync-master
    log_info "프로젝트 복사 완료"
else
    log_warn "Windows 프로젝트를 찾을 수 없습니다"
    log_info "수동으로 프로젝트를 복사하세요"
fi

# 7. Python 가상환경 설정
log_info "Python 가상환경 설정 중..."
if [ -d "data-sync-master" ]; then
    cd data-sync-master
    if [ -f "src/requirements.txt" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r src/requirements.txt
        log_info "Python 가상환경 설정 완료"
    else
        log_warn "requirements.txt 파일을 찾을 수 없습니다"
    fi
else
    log_warn "프로젝트 디렉토리를 찾을 수 없습니다"
fi

# 8. 스크립트 실행 권한 설정
log_info "스크립트 실행 권한 설정 중..."
if [ -d "data-sync-master/scripts" ]; then
    chmod +x data-sync-master/scripts/dev/*.sh
    chmod +x data-sync-master/scripts/*.sh
    log_info "스크립트 권한 설정 완료"
fi

# 9. WSL 설정 파일 생성
log_info "WSL 성능 최적화 설정 중..."
cat > ~/.wslconfig << EOF
[wsl2]
memory=6GB
processors=4
swap=2GB
localhostForwarding=true
EOF
log_info "WSL 설정 파일 생성 완료"

# 10. bashrc 설정
log_info "bashrc 설정 중..."
cat >> ~/.bashrc << 'EOF'

# 개발 환경 설정
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$HOME/projects/data-sync-master/src:$PYTHONPATH"

# 별칭 설정
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# 프로젝트 디렉토리로 이동
alias proj='cd ~/projects/data-sync-master'
alias dev='cd ~/projects/data-sync-master && ./scripts/dev/start-dev.sh'
alias sync='cd ~/projects/data-sync-master && ./scripts/dev/auto-sync.sh'

# Git 별칭
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline'

echo "개발 환경이 설정되었습니다!"
echo "사용 가능한 명령어:"
echo "  proj  - 프로젝트 디렉토리로 이동"
echo "  dev   - 개발 환경 시작"
echo "  sync  - 자동 동기화 시작"
echo "  gs    - git status"
echo "  ga    - git add ."
echo "  gc    - git commit -m"
echo "  gp    - git push"
EOF

log_info "bashrc 설정 완료"

echo
echo "========================================"
echo "WSL 사용자 설정 완료!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. 터미널을 재시작하거나 다음 명령어를 실행하세요:"
echo "   source ~/.bashrc"
echo
echo "2. Docker Desktop을 설치하고 WSL2 백엔드를 활성화하세요"
echo "3. Cursor를 설치하고 WSL 확장을 활성화하세요"
echo "4. 개발 환경을 시작하세요:"
echo "   cd ~/projects/data-sync-master"
echo "   ./scripts/dev/start-dev.sh"
echo
echo "사용 가능한 명령어:"
echo "  proj  - 프로젝트 디렉토리로 이동"
echo "  dev   - 개발 환경 시작"
echo "  sync  - 자동 동기화 시작"
echo "========================================" 