# 🚀 운영 배포 가이드

## 🎯 운영 환경 개요

### ✅ 운영 환경 특징
- 최적화된 Docker 이미지
- 보안 강화 설정
- 성능 최적화
- 로그 관리
- 자동 재시작

### ✅ 운영 환경 구조
```
📁 운영 환경
├── 📄 docker/Dockerfile.prod         # 운영용 Docker 이미지
├── 📄 docker/docker-compose.prod.yml # 운영용 Docker Compose
├── 📄 scripts/prod/build-prod.bat    # 운영 이미지 빌드
├── 📄 scripts/prod/start-prod.bat    # 운영 환경 시작
└── 📄 config/env.prod                # 운영용 환경변수
```

## 🚀 운영 배포 워크플로우

### 1단계: 코드 준비
```bash
# 개발 완료된 코드 확인
git status
git log --oneline -5
```

### 2단계: 운영 이미지 빌드
```bash
# 운영용 Docker 이미지 빌드
.\scripts\prod\build-prod.bat
```

### 3단계: 운영 환경 배포
```bash
# 운영 환경 시작
.\scripts\prod\start-prod.bat
```

### 4단계: 배포 확인
```bash
# 서비스 상태 확인
docker-compose -f docker/docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs -f web
```

## 🛠️ 운영 환경 관리

### 운영 환경 시작
```bash
# 운영용 이미지 빌드 및 시작
.\scripts\prod\build-prod.bat
.\scripts\prod\start-prod.bat
```

### 운영 환경 중지
```bash
# 운영 환경 중지
docker-compose -f docker/docker-compose.prod.yml down
```

### 운영 환경 재시작
```bash
# 운영 환경 재시작
docker-compose -f docker/docker-compose.prod.yml restart
```

### 운영 로그 확인
```bash
# 전체 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs

# 실시간 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs -f web

# 특정 서비스 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs postgres
docker-compose -f docker/docker-compose.prod.yml logs redis
```

## 🔒 운영 환경 보안

### 1. 환경변수 관리
```bash
# 운영용 환경변수 설정
# config/env.prod 파일에서 설정
POSTGRES_PASSWORD=강력한_비밀번호
FLASK_ENV=production
FLASK_DEBUG=0
```

### 2. 네트워크 보안
- 방화벽 설정
- 포트 제한
- SSL/TLS 설정 (필요시)

### 3. 데이터베이스 보안
- 강력한 비밀번호 사용
- 접근 권한 제한
- 정기적인 백업

## 📊 운영 모니터링

### 서비스 상태 확인
```bash
# 컨테이너 상태 확인
docker ps

# 리소스 사용량 확인
docker stats

# 디스크 사용량 확인
docker system df
```

### 로그 모니터링
```bash
# 실시간 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs -f

# 로그 파일 크기 확인
docker system df -v
```

### 성능 모니터링
```bash
# 컨테이너 성능 확인
docker stats --no-stream

# 메모리 사용량 확인
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 🔄 업데이트 프로세스

### 1. 코드 업데이트
```bash
# 최신 코드 가져오기
git pull origin main

# 변경사항 확인
git log --oneline -3
```

### 2. 이미지 재빌드
```bash
# 운영용 이미지 재빌드
.\scripts\prod\build-prod.bat
```

### 3. 운영 환경 재배포
```bash
# 운영 환경 재시작
.\scripts\prod\start-prod.bat
```

### 4. 배포 확인
```bash
# 서비스 상태 확인
docker-compose -f docker/docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker/docker-compose.prod.yml logs -f web
```

## 💾 백업 및 복구

### 데이터베이스 백업
```bash
# PostgreSQL 백업
docker exec data-sync-postgres-prod pg_dump -U postgres fs_master_web > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis 백업
docker exec data-sync-redis-prod redis-cli BGSAVE
```

### 데이터베이스 복구
```bash
# PostgreSQL 복구
docker exec -i data-sync-postgres-prod psql -U postgres fs_master_web < backup_file.sql

# Redis 복구
docker exec data-sync-redis-prod redis-cli FLUSHALL
```

## 🚨 문제 해결

### 운영 환경이 시작되지 않을 때
1. **이미지 확인**: `docker images | findstr data-sync-web`
2. **포트 충돌 확인**: `netstat -an | findstr :5000`
3. **로그 확인**: `docker-compose -f docker/docker-compose.prod.yml logs`

### 성능 문제가 발생할 때
1. **리소스 사용량 확인**: `docker stats`
2. **로그 확인**: `docker-compose -f docker/docker-compose.prod.yml logs`
3. **데이터베이스 성능 확인**: PostgreSQL 쿼리 분석

### 보안 문제가 발생할 때
1. **환경변수 확인**: `docker-compose -f docker/docker-compose.prod.yml config`
2. **네트워크 설정 확인**: `docker network ls`
3. **로그 분석**: 보안 관련 로그 확인

## 📞 운영 지원

### 긴급 상황 대응
1. **서비스 중지**: `docker-compose -f docker/docker-compose.prod.yml down`
2. **로그 분석**: `docker-compose -f docker/docker-compose.prod.yml logs`
3. **백업 복구**: 데이터베이스 백업에서 복구

### 정기 점검
1. **일일 점검**: 서비스 상태, 로그 확인
2. **주간 점검**: 성능 분석, 백업 확인
3. **월간 점검**: 보안 업데이트, 시스템 최적화

## 💡 운영 팁

### 1. 자동화 스크립트
```bash
# 운영 환경 자동 시작 스크립트
@echo off
echo 운영 환경 시작 중...
call .\scripts\prod\build-prod.bat
call .\scripts\prod\start-prod.bat
echo 운영 환경 시작 완료!
```

### 2. 모니터링 스크립트
```bash
# 상태 확인 스크립트
@echo off
echo === 운영 환경 상태 ===
docker-compose -f docker/docker-compose.prod.yml ps
echo.
echo === 리소스 사용량 ===
docker stats --no-stream
```

### 3. 백업 스크립트
```bash
# 자동 백업 스크립트
@echo off
echo 데이터베이스 백업 중...
docker exec data-sync-postgres-prod pg_dump -U postgres fs_master_web > backup_%date:~0,4%%date:~5,2%%date:~8,2%.sql
echo 백업 완료!
``` 