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
        docker-compose -f ../../docker/docker-compose.wsl.yml restart web
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 업데이트 완료!"
    else
        echo "변경사항 없음"
    fi
    
    echo "5초 후 다시 확인..."
    sleep 5
done 