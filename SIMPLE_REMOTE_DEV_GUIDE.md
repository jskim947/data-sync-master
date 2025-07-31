# 🚀 간단한 원격 개발 가이드

SSH 설정 없이 Git을 사용한 간단하고 안정적인 원격 개발 방법입니다.

## 🎯 권장 방법: Git 기반 개발

### 장점:
- ✅ SSH 설정 불필요
- ✅ 안정적이고 신뢰할 수 있음
- ✅ 버전 관리와 함께 안전한 배포
- ✅ 여러 개발자 동시 작업 가능
- ✅ 롤백 가능

### 단점:
- ❌ Git 작업 필요
- ❌ 약간의 지연 시간

## 🖥️ 서버 설정 (현재 컴퓨터)

### 1단계: 개발 환경 시작
```bash
# 간단한 개발 환경 시작
simple-remote-dev.bat
```

또는 수동으로:
```bash
# Docker 개발 환경 시작
docker-compose -f docker-compose.remote-dev.yml up --build -d

# 상태 확인
docker-compose -f docker-compose.remote-dev.yml ps
```

### 2단계: 자동 재시작 설정 (선택사항)
```bash
# 파일 변경 감지 및 자동 재시작
watch-and-restart.sh
```

## 💻 클라이언트 설정 (다른 컴퓨터)

### 1단계: 프로젝트 클론
```bash
git clone https://github.com/jskim947/data-sync-master.git
cd data-sync-master
```

### 2단계: 개발 환경 설정
```bash
# Python 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정
`.env` 파일 생성:
```bash
DATABASE_URL=postgresql://postgres:infomax@서버IP:5432/fs_master_web
REDIS_URL=redis://서버IP:6379/0
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🔄 개발 워크플로우

### 방법 1: Git 기반 (권장)
```bash
# 1. 로컬에서 코드 수정

# 2. Git 커밋 및 푸시
git add .
git commit -m "코드 수정 내용"
git push origin main

# 3. 서버에서 업데이트
git pull origin main
docker-compose -f docker-compose.remote-dev.yml restart web
```

### 방법 2: 자동 동기화
```bash
# 서버에서 자동 감지 스크립트 실행
./watch-and-restart.sh
```

## 🌐 접속 정보

- **웹 애플리케이션**: `http://172.27.64.1:5000`
- **PostgreSQL**: `172.27.64.1:5432`
- **Redis**: `172.27.64.1:6379`

## 🛠️ 유용한 명령어

### 서버 관리
```bash
# 상태 확인
docker-compose -f docker-compose.remote-dev.yml ps

# 로그 확인
docker-compose -f docker-compose.remote-dev.yml logs -f web

# 재시작
docker-compose -f docker-compose.remote-dev.yml restart web

# 완전 재빌드
docker-compose -f docker-compose.remote-dev.yml up --build -d

# 종료
docker-compose -f docker-compose.remote-dev.yml down
```

### 개발 도구
```bash
# 로컬 테스트
python app.py --debug

# 데이터베이스 연결 테스트
python test_db_connection.py

# 마이그레이션 도구 테스트
python fs_migration_tool.py --help
```

## 📋 빠른 시작 체크리스트

### 서버에서:
- [ ] `simple-remote-dev.bat` 실행
- [ ] 웹 애플리케이션 접속 확인: `http://172.27.64.1:5000`
- [ ] (선택) `watch-and-restart.sh` 실행

### 클라이언트에서:
- [ ] 프로젝트 클론: `git clone https://github.com/jskim947/data-sync-master.git`
- [ ] 가상환경 설정 및 의존성 설치
- [ ] `.env` 파일 생성
- [ ] 코드 수정 및 Git 푸시

## 🚨 문제 해결

### 웹 애플리케이션에 접속이 안 될 때:
1. **Docker 상태 확인**: `docker ps`
2. **포트 확인**: `netstat -an | findstr :5000`
3. **방화벽 확인**: Windows 방화벽에서 포트 5000 허용

### Git 동기화가 안 될 때:
1. **Git 상태 확인**: `git status`
2. **원격 저장소 확인**: `git remote -v`
3. **네트워크 연결 확인**: `ping github.com`

### 데이터베이스 연결이 안 될 때:
1. **PostgreSQL 컨테이너 상태**: `docker-compose ps postgres`
2. **포트 확인**: `netstat -an | findstr :5432`
3. **환경 변수 확인**: `.env` 파일의 DATABASE_URL

## 💡 팁

1. **자주 사용하는 명령어는 별칭 설정**:
   ```bash
   alias dev-up='docker-compose -f docker-compose.remote-dev.yml up -d'
   alias dev-down='docker-compose -f docker-compose.remote-dev.yml down'
   alias dev-restart='docker-compose -f docker-compose.remote-dev.yml restart web'
   ```

2. **VS Code에서 Git 작업 자동화**:
   - Git Graph 확장 설치
   - GitLens 확장 설치
   - 자동 커밋 및 푸시 설정

3. **브라우저 북마크 설정**:
   - 웹 애플리케이션: `http://172.27.64.1:5000`
   - Git 저장소: `https://github.com/jskim947/data-sync-master`

## 📞 지원

문제가 발생하면:
1. Docker 로그 확인: `docker-compose logs web`
2. Git 상태 확인: `git status`
3. 네트워크 연결 확인: `ping 172.27.64.1` 