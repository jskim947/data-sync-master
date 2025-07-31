#!/bin/bash

# FS Master Web Application Docker 시작 스크립트

echo "🚀 FS Master Web Application 시작 중..."

# Docker Compose로 모든 서비스 시작
echo "📦 Docker 컨테이너 빌드 및 시작..."
docker-compose up --build -d

# 서비스 상태 확인
echo "🔍 서비스 상태 확인 중..."
sleep 10

# PostgreSQL 연결 확인
echo "🗄️ PostgreSQL 연결 확인..."
docker-compose exec postgres pg_isready -U postgres

# 웹 애플리케이션 상태 확인
echo "🌐 웹 애플리케이션 상태 확인..."
curl -f http://localhost:5000/ || echo "웹 애플리케이션이 아직 시작되지 않았습니다."

echo ""
echo "✅ 모든 서비스가 시작되었습니다!"
echo "🌐 웹 애플리케이션: http://localhost:5000"
echo "🗄️ PostgreSQL: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo ""
echo "📋 유용한 명령어:"
echo "  - 로그 확인: docker-compose logs -f"
echo "  - 서비스 중지: docker-compose down"
echo "  - 서비스 재시작: docker-compose restart" 