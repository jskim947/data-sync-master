# 🚀 Data Sync Master 원격 개발 환경 설정 가이드

이 가이드는 다른 컴퓨터에서 Docker로 애플리케이션을 실행하고, 현재 컴퓨터에서 코딩하는 원격 개발 환경을 설정하는 방법을 설명합니다.

## 📋 사전 준비사항

### 다른 컴퓨터 (서버)에서 필요한 것
- Docker 및 Docker Compose 설치
- Git 설치
- 포트 5000, 5432, 6379 사용 가능

### 현재 컴퓨터 (개발)에서 필요한 것
- 코드 에디터 (VS Code, Cursor 등)
- Git 설치
- SSH 접속 가능 (선택사항)

## 🖥️ 서버 컴퓨터 설정 (다른 컴퓨터)

### 1. 프로젝트 클론
```bash
git clone https://github.com/datasolution-team/data-sync-master.git
cd data-sync-master
```

### 2. JDBC 드라이버 준비 (필요한 경우)
```bash
# jdbc-drivers 폴더에 필요한 .jar 파일 배치
mkdir -p jdbc-drivers
# ifxjdbc.jar, Altibase.jar 등을 복사
```

### 3. 원격 개발 환경 시작
**Windows:**
```bash
start-remote-dev.bat
```

**Linux/Mac:**
```bash
chmod +x start-remote-dev.sh
./start-remote-dev.sh
```

**수동 실행:**
```bash
docker-compose -f docker-compose.remote-dev.yml up --build -d
```

### 4. 접속 확인
브라우저에서 `http://서버IP:5000` 접속하여 애플리케이션이 정상 작동하는지 확인

## 💻 개발 컴퓨터 설정 (현재 컴퓨터)

### 1. 프로젝트 클론
```bash
git clone https://github.com/datasolution-team/data-sync-master.git
cd data-sync-master
```

### 2. 개발 환경 설정
로컬에서 코드를 수정하고 테스트할 수 있도록 설정:

**Python 가상환경 생성 (권장):**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

**의존성 설치:**
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일 생성:
```bash
# .env 파일 생성
DATABASE_URL=postgresql://postgres:infomax@서버IP:5432/fs_master_web
REDIS_URL=redis://서버IP:6379/0
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🔄 개발 워크플로우

### 1. 코드 수정
현재 컴퓨터에서 코드를 수정합니다.

### 2. 코드 테스트 (로컬)
```bash
# 로컬에서 테스트 (서버 DB 사용)
python app.py --debug
```

### 3. 코드 배포
수정된 코드를 서버에 배포:

**Git을 통한 배포:**
```bash
git add .
git commit -m "코드 수정 내용"
git push origin main
```

**서버에서 업데이트:**
```bash
# 서버에서
git pull origin main
docker-compose -f docker-compose.remote-dev.yml up --build -d
```

### 4. 빠른 재배포 (선택사항)
서버에서 코드 변경 시 자동 재빌드를 위한 스크립트:

**watch-and-rebuild.sh (서버용):**
```bash
#!/bin/bash
while inotifywait -r -e modify,create,delete .; do
    echo "코드 변경 감지, 재빌드 시작..."
    docker-compose -f docker-compose.remote-dev.yml up --build -d
    echo "재빌드 완료!"
done
```

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

## 🔧 고급 설정

### 1. SSH 터널링 (보안 강화)
```bash
# 로컬에서 서버로 SSH 터널 생성
ssh -L 5000:localhost:5000 -L 5432:localhost:5432 -L 6379:localhost:6379 user@서버IP
```

### 2. 자동 동기화 (rsync)
```bash
# 코드 변경 시 자동 동기화
rsync -avz --exclude='.git' --exclude='__pycache__' ./ user@서버IP:/path/to/data-sync-master/
```

### 3. Docker Registry 사용
```bash
# 이미지를 레지스트리에 푸시
docker build -f Dockerfile.remote-dev -t your-registry/data-sync-master:latest .
docker push your-registry/data-sync-master:latest

# 서버에서 레지스트리 이미지 사용
# docker-compose.remote-dev.yml에서 image: your-registry/data-sync-master:latest 사용
```

## 🚨 주의사항

1. **보안**: 서버의 방화벽 설정을 확인하고 필요한 포트만 열어두세요.
2. **백업**: 중요한 데이터는 정기적으로 백업하세요.
3. **버전 관리**: 모든 코드 변경사항을 Git으로 관리하세요.
4. **환경 분리**: 개발/테스트/프로덕션 환경을 분리하여 관리하세요.

## 📞 문제 해결

### 일반적인 문제들

1. **포트 충돌**: 다른 서비스가 같은 포트를 사용하고 있는지 확인
2. **네트워크 연결**: 서버와 개발 컴퓨터 간 네트워크 연결 확인
3. **권한 문제**: Docker 실행 권한 및 파일 권한 확인
4. **메모리 부족**: Docker 컨테이너의 메모리 사용량 모니터링

### 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.remote-dev.yml logs

# 실시간 로그
docker-compose -f docker-compose.remote-dev.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.remote-dev.yml logs web
``` 