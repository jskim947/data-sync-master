#!/bin/bash

echo "🚀 FS Master 개발 환경 빠른 재시작"
echo

echo "📦 기존 컨테이너 중지..."
docker-compose -f docker-compose.dev.yml down

echo "🔄 컨테이너 재시작 (빌드 없이)..."
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ 서비스 시작 대기..."
sleep 5

echo "🔍 서비스 상태 확인..."
docker-compose -f docker-compose.dev.yml ps

echo
echo "✅ 재시작 완료!"
echo "🌐 웹 애플리케이션: http://localhost:5000"
echo "📊 PostgreSQL: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo
echo "💡 코드 변경사항은 자동으로 반영됩니다!"
echo "💡 전체 재빌드가 필요한 경우: docker-compose -f docker-compose.dev.yml up --build -d" 