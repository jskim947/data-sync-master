# 🛠️ 개발 환경 가이드

## 🚀 빠른 시작

### 1. 개발 환경 시작
```bash
# 개발 환경 시작 (볼륨 마운트, 실시간 반영)
.\scripts\dev\start-dev.bat
```

### 2. Git 자동 동기화 시작
```bash
# Git 푸시 시 자동으로 반영
.\scripts\dev\auto-sync.bat
```

## 🔧 개발 환경 특징

### ✅ 실시간 코드 반영
- 소스 코드 볼륨 마운트
- 코드 수정 시 즉시 반영
- 핫 리로드 지원

### ✅ 디버그 모드
- 상세한 로그 출력
- 디버그 정보 표시
- 개발자 도구 활성화

### ✅ Git 자동 동기화
- 클라이언트에서 Git 푸시
- 서버에서 자동 감지
- Docker 컨테이너 자동 재시작

## 📁 개발 환경 구조

```
📁 개발 환경
├── 📄 docker/Dockerfile.dev          # 개발용 Docker 이미지
├── 📄 docker/docker-compose.dev.yml  # 개발용 Docker Compose
├── 📄 scripts/dev/start-dev.bat      # 개발 환경 시작
├── 📄 scripts/dev/auto-sync.bat      # Git 자동 동기화
└── 📄 config/env.dev                 # 개발용 환경변수
```

## 🔄 개발 워크플로우

### 1. 로컬 개발
```bash
# 코드 수정
# 파일 저장
```

### 2. Git 커밋
```bash
git add .
git commit -m "개발 내용"
```

### 3. Git 푸시 (자동 반영)
```bash
git push origin main
```

### 4. 서버에서 자동 처리
- Git 변경사항 감지
- 코드 자동 다운로드
- Docker 컨테이너 재시작
- 웹 애플리케이션 업데이트

## 🌐 접속 정보

- **웹 애플리케이션**: `http://localhost:5000`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

## 🛠️ 유용한 명령어

### 개발 환경 관리
```bash
# 개발 환경 시작
.\scripts\dev\start-dev.bat

# 개발 환경 중지
docker-compose -f docker/docker-compose.dev.yml down

# 개발 환경 재시작
docker-compose -f docker/docker-compose.dev.yml restart

# 개발 로그 확인
docker-compose -f docker/docker-compose.dev.yml logs -f web
```

### 데이터베이스 관리
```bash
# PostgreSQL 접속
docker exec -it data-sync-postgres-dev psql -U postgres -d fs_master_web

# Redis 접속
docker exec -it data-sync-redis-dev redis-cli
```

### 코드 테스트
```bash
# 데이터베이스 연결 테스트
python test_db_connection.py

# 마이그레이션 도구 테스트
python fs_migration_tool.py --help
```

## 🚨 문제 해결

### 개발 환경이 시작되지 않을 때
1. **Docker 상태 확인**: `docker ps`
2. **포트 충돌 확인**: `netstat -an | findstr :5000`
3. **로그 확인**: `docker-compose -f docker/docker-compose.dev.yml logs`

### 코드 변경이 반영되지 않을 때
1. **볼륨 마운트 확인**: `docker inspect data-sync-web-dev`
2. **컨테이너 재시작**: `docker-compose -f docker/docker-compose.dev.yml restart web`
3. **Git 상태 확인**: `git status`

### Git 자동 동기화가 안 될 때
1. **Git 연결 확인**: `git fetch origin main`
2. **브랜치 확인**: `git branch`
3. **권한 확인**: GitHub 저장소 접근 권한

## 💡 개발 팁

### 1. VS Code 설정
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.formatting.provider": "black"
}
```

### 2. 브라우저 북마크
- 개발 서버: `http://localhost:5000`
- Git 저장소: `https://github.com/jskim947/data-sync-master`

### 3. 자주 사용하는 명령어 별칭
```bash
alias dev-start='.\scripts\dev\start-dev.bat'
alias dev-logs='docker-compose -f docker/docker-compose.dev.yml logs -f web'
alias dev-restart='docker-compose -f docker/docker-compose.dev.yml restart web'
```

## 📞 지원

문제가 발생하면:
1. Docker 로그 확인
2. Git 상태 확인
3. 네트워크 연결 확인
4. 포트 충돌 확인 