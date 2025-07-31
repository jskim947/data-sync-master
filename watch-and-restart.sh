#!/bin/bash

echo "========================================"
echo "파일 변경 감지 및 자동 재시작"
echo "========================================"
echo

# inotify-tools 설치 확인
if ! command -v inotifywait &> /dev/null; then
    echo "inotify-tools가 설치되지 않았습니다."
    echo "설치: sudo apt-get install inotify-tools"
    exit 1
fi

echo "파일 변경 감지 시작... (Ctrl+C로 종료)"
echo "감시 대상: app.py, templates/, db_connection_test/"
echo

while inotifywait -r -e modify,create,delete \
    app.py \
    templates/ \
    db_connection_test/ \
    --exclude '.*\.pyc$' \
    --exclude '__pycache__' \
    --exclude '\.git'; do
    
    echo
    echo "========================================"
    echo "$(date): 파일 변경 감지!"
    echo "========================================"
    
    echo "1. Git pull 실행..."
    git pull origin main
    
    echo "2. 웹 서버 재시작..."
    docker-compose -f docker-compose.remote-dev.yml restart web
    
    echo "3. 재시작 완료! $(date)"
    echo "========================================"
    echo
done 