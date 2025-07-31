#!/bin/bash

echo "========================================"
echo "FS Master 원격 개발 환경 시작"
echo "========================================"
echo

echo "1. 기존 컨테이너 정리..."
docker-compose -f docker-compose.remote-dev.yml down

echo
echo "2. 이미지 빌드 및 컨테이너 시작..."
docker-compose -f docker-compose.remote-dev.yml up --build -d

echo
echo "3. 컨테이너 상태 확인..."
docker-compose -f docker-compose.remote-dev.yml ps

echo
echo "4. 로그 확인 (Ctrl+C로 종료)..."
echo "========================================"
docker-compose -f docker-compose.remote-dev.yml logs -f web

echo
echo "========================================"
echo "원격 개발 환경이 시작되었습니다!"
echo "웹 애플리케이션: http://localhost:5000"
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"
echo "========================================"
echo
echo "명령어:"
echo "- 로그 확인: docker-compose -f docker-compose.remote-dev.yml logs -f web"
echo "- 재시작: docker-compose -f docker-compose.remote-dev.yml restart web"
echo "- 종료: docker-compose -f docker-compose.remote-dev.yml down"
echo "- 재빌드: docker-compose -f docker-compose.remote-dev.yml up --build -d"
echo "========================================" 