# 🔄 Git 기반 자동 동기화 시스템

SSH 설정 없이 Git을 사용한 간단하고 안정적인 원격 개발 시스템입니다.

## 🎯 시스템 개요

### 장점:
- ✅ SSH 설정 불필요
- ✅ 안정적이고 신뢰할 수 있음
- ✅ 버전 관리와 함께 안전한 배포
- ✅ 여러 개발자 동시 작업 가능
- ✅ 자동 동기화로 실시간 반영
- ✅ 롤백 가능

### 워크플로우:
1. **클라이언트**: 코드 수정 → Git 커밋 → Git 푸시
2. **서버**: 자동 감지 → Git 풀 → Docker 재시작
3. **결과**: 즉시 웹 애플리케이션에 반영

## 🖥️ 서버 설정

### 1단계: SSH 설정 정리
```bash
# SSH 관련 설정 정리
.\cleanup-ssh.bat
```

### 2단계: 자동 동기화 시스템 시작
```bash
# Git 기반 자동 동기화 시작
.\auto-sync-system.bat
```

### 3단계: 수동 실행 (선택사항)
```bash
# 개발 환경 시작
docker-compose -f docker-compose.remote-dev.yml up --build -d

# 수동 동기화
git pull origin main
docker-compose -f docker-compose.remote-dev.yml restart web
```

## 💻 클라이언트 설정

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
DATABASE_URL=postgresql://postgres:infomax@10.150.2.150:5432/fs_master_web
REDIS_URL=redis://10.150.2.150:6379/0
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🔄 개발 워크플로우

### 클라이언트에서:
```bash
# 1. 코드 수정

# 2. 변경사항 확인
git status

# 3. 파일 추가
git add .

# 4. 커밋
git commit -m "코드 수정 내용"

# 5. 푸시 (자동으로 서버에 반영됨)
git push origin main
```

### 서버에서 (자동):
- Git 변경사항 자동 감지
- 코드 자동 다운로드
- Docker 컨테이너 자동 재시작
- 웹 애플리케이션 즉시 업데이트

## 🌐 접속 정보

- **웹 애플리케이션**: `http://10.150.2.150:5000`
- **PostgreSQL**: `10.150.2.150:5432`
- **Redis**: `10.150.2.150:6379`

## 🛠️ 유용한 명령어

### 서버 관리
```bash
# 자동 동기화 시작
.\auto-sync-system.bat

# 수동 동기화
git pull origin main && docker-compose -f docker-compose.remote-dev.yml restart web

# 개발 환경 상태 확인
docker-compose -f docker-compose.remote-dev.yml ps

# 로그 확인
docker-compose -f docker-compose.remote-dev.yml logs -f web
```

### 클라이언트 개발
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
- [ ] `.\cleanup-ssh.bat` 실행 (SSH 정리)
- [ ] `.\auto-sync-system.bat` 실행 (자동 동기화 시작)
- [ ] 웹 애플리케이션 접속 확인: `http://10.150.2.150:5000`

### 클라이언트에서:
- [ ] 프로젝트 클론: `git clone https://github.com/jskim947/data-sync-master.git`
- [ ] 가상환경 설정 및 의존성 설치
- [ ] `.env` 파일 생성
- [ ] 코드 수정 및 Git 푸시

## 🚨 문제 해결

### 자동 동기화가 안 될 때:
1. **Git 연결 확인**: `git fetch origin main`
2. **Docker 상태 확인**: `docker ps`
3. **로그 확인**: `docker-compose logs web`

### 웹 애플리케이션에 접속이 안 될 때:
1. **Docker 상태 확인**: `docker-compose ps`
2. **포트 확인**: `netstat -an | findstr :5000`
3. **방화벽 확인**: Windows 방화벽에서 포트 5000 허용

### Git 동기화가 안 될 때:
1. **Git 상태 확인**: `git status`
2. **원격 저장소 확인**: `git remote -v`
3. **네트워크 연결 확인**: `ping github.com`

## 💡 팁

1. **자주 사용하는 명령어는 별칭 설정**:
   ```bash
   alias dev-sync='git add . && git commit -m "자동 동기화" && git push'
   alias dev-status='docker-compose -f docker-compose.remote-dev.yml ps'
   ```

2. **VS Code에서 Git 작업 자동화**:
   - Git Graph 확장 설치
   - GitLens 확장 설치
   - 자동 커밋 및 푸시 설정

3. **브라우저 북마크 설정**:
   - 웹 애플리케이션: `http://10.150.2.150:5000`
   - Git 저장소: `https://github.com/jskim947/data-sync-master`

## 📞 지원

문제가 발생하면:
1. Docker 로그 확인: `docker-compose logs web`
2. Git 상태 확인: `git status`
3. 네트워크 연결 확인: `ping 10.150.2.150`

## 🔒 보안

1. **Git 저장소 보안**: GitHub 저장소 접근 권한 관리
2. **환경 변수 보안**: `.env` 파일에 민감한 정보 포함 금지
3. **정기적인 백업**: 중요한 데이터는 정기적으로 백업 