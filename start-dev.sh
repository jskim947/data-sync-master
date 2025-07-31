#!/bin/bash

echo "🚀 FS Master 개발 환경 시작 중..."
echo

echo "📦 Docker Compose 개발 환경 시작..."
docker-compose -f docker-compose.dev.yml up --build -d

echo
echo "⏳ 서비스 시작 대기 중..."
sleep 10

echo
echo "📊 서비스 상태 확인..."
docker-compose -f docker-compose.dev.yml ps

echo
echo "🌐 웹 애플리케이션 접속 주소:"
echo "   http://localhost:5000"
echo
echo "📝 개발 모드 특징:"
echo "   - 코드 변경 시 자동 리로드"
echo "   - 실시간 에러 메시지"
echo "   - 디버그 모드 활성화"
echo
echo "🛑 종료하려면: docker-compose -f docker-compose.dev.yml down"
echo 