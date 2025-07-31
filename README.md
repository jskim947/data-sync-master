# 🚀 Data Sync Master - 데이터 동기화 마스터

데이터솔루션부에서 사용하는 데이터 동기화 및 마이그레이션 도구입니다. `db_connection_test`를 import하여 다양한 데이터베이스 간 데이터 동기화를 지원합니다.

## 📁 프로젝트 구조

```
data-sync-master/
├── README.md                    # 프로젝트 설명
├── REMOTE_DEV_SETUP.md          # 원격 개발 환경 설정 가이드
├── app.py                       # 웹 애플리케이션 메인 파일
├── setup.py                     # 초기 설정 스크립트
├── fs_migration_tool.py         # CLI 마이그레이션 도구
├── fs_migration_example.py      # 마이그레이션 예시
├── requirements.txt            # 의존성 목록
├── docker-compose.yml          # 프로덕션용 Docker Compose
├── docker-compose.dev.yml      # 개발용 Docker Compose
├── docker-compose.remote-dev.yml # 원격 개발용 Docker Compose
├── Dockerfile                  # 기본 Dockerfile
├── Dockerfile.remote-dev       # 원격 개발용 Dockerfile
├── start-dev.bat               # Windows 개발 환경 시작 스크립트
├── start-dev.sh                # Linux/Mac 개발 환경 시작 스크립트
├── start-remote-dev.bat        # Windows 원격 개발 환경 시작 스크립트
├── start-remote-dev.sh         # Linux/Mac 원격 개발 환경 시작 스크립트
├── restart-dev.bat             # Windows 빠른 재시작 스크립트
├── restart-dev.sh              # Linux/Mac 빠른 재시작 스크립트
├── restart-remote-dev.bat      # Windows 원격 개발 재시작 스크립트
├── restart-remote-dev.sh       # Linux/Mac 원격 개발 재시작 스크립트
├── jdbc-drivers/               # JDBC 드라이버 폴더
│   ├── README.md               # JDBC 드라이버 설명
│   ├── ifxjdbc.jar            # Informix JDBC 드라이버 (별도 다운로드)
│   └── Altibase.jar           # Altibase JDBC 드라이버 (별도 다운로드)
├── templates/                  # 웹 템플릿
│   ├── base.html
│   ├── dashboard.html
│   ├── query.html
│   ├── servers.html
│   └── add_server.html
└── db_connection_test/         # db_connection_test 패키지
    ├── __init__.py
    ├── setup.py
    ├── requirements.txt
    ├── README_PACKAGE.md
    ├── db_servers.ini          # 메인 설정 파일
    ├── db_servers.template.ini # 설정 파일 템플릿
    └── simple_db_migrator/
        ├── __init__.py
        ├── connector.py
        └── cli.py
```

## 🚀 빠른 시작 (Docker)

### 사전 준비 (JDBC 드라이버)

Informix나 Altibase를 사용하려면 JDBC 드라이버를 다운로드해야 합니다:

1. **`jdbc-drivers/` 폴더 생성**
2. **Informix JDBC 드라이버 다운로드**: `ifxjdbc.jar` → `jdbc-drivers/` 폴더에 저장
3. **Altibase JDBC 드라이버 다운로드**: `Altibase.jar` → `jdbc-drivers/` 폴더에 저장

자세한 다운로드 방법은 `jdbc-drivers/README.md`를 참조하세요.

### 개발 환경 (권장)

개발 환경에서는 코드 변경 시 자동으로 리로드되어 즉시 반영됩니다.

**Windows:**
```bash
start-dev.bat
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**수동 실행:**
```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

### 원격 개발 환경

다른 컴퓨터에서 Docker로 실행하고, 현재 컴퓨터에서 코딩하는 환경입니다.

**서버 컴퓨터에서:**
```bash
# Windows
start-remote-dev.bat

# Linux/Mac
chmod +x start-remote-dev.sh
./start-remote-dev.sh
```

**개발 컴퓨터에서:**
- 코드 수정 후 Git으로 배포
- 서버에서 `git pull` 후 재빌드

자세한 설정 방법은 `REMOTE_DEV_SETUP.md`를 참조하세요.

### 프로덕션 환경

```bash
docker-compose up --build -d
```

### 접속

브라우저에서 **http://localhost:5000** 접속

## 🛠️ 개발 환경 특징

### 로컬 개발 환경
- ✅ **자동 리로드**: 코드 변경 시 즉시 반영
- ✅ **실시간 에러 메시지**: 디버그 모드로 상세한 에러 정보
- ✅ **볼륨 마운트**: 로컬 파일과 컨테이너 동기화
- ✅ **핫 리로드**: Flask 개발 서버의 자동 리로드 기능
- ✅ **JDBC 드라이버 지원**: Informix, Altibase 연결 지원

### 원격 개발 환경
- ✅ **정적 빌드**: 안정적인 프로덕션 환경과 유사한 구성
- ✅ **Git 기반 배포**: 버전 관리와 함께 안전한 배포
- ✅ **환경 분리**: 개발/서버 환경 완전 분리
- ✅ **확장성**: 여러 개발자가 동시 작업 가능

## 📝 개발 팁

### 로컬 개발
1. **코드 수정**: `app.py`, `templates/`, `db_connection_test/` 파일을 수정하면 자동으로 반영됩니다.
2. **빠른 재시작**: `restart-dev.bat` (Windows) 또는 `./restart-dev.sh` (Linux/Mac)으로 재빌드 없이 재시작
3. **로그 확인**: `docker-compose -f docker-compose.dev.yml logs web`으로 실시간 로그 확인
4. **재시작**: `docker-compose -f docker-compose.dev.yml restart web`으로 웹 서버만 재시작
5. **종료**: `docker-compose -f docker-compose.dev.yml down`으로 모든 서비스 종료
6. **전체 재빌드**: `docker-compose -f docker-compose.dev.yml up --build -d` (의존성 변경 시에만 필요)

### 원격 개발
1. **코드 수정**: 로컬에서 코드 수정 후 Git 커밋
2. **배포**: `git push` 후 서버에서 `git pull` 및 재빌드
3. **빠른 재시작**: `restart-remote-dev.bat` (Windows) 또는 `./restart-remote-dev.sh` (Linux/Mac)
4. **로그 확인**: `docker-compose -f docker-compose.remote-dev.yml logs -f web`
5. **재빌드**: `docker-compose -f docker-compose.remote-dev.yml up --build -d`

## 🔧 JDBC 드라이버 설정

### PostgreSQL만 사용하는 경우
- JDBC 드라이버가 필요하지 않습니다
- 바로 개발 환경을 시작할 수 있습니다

### Informix/Altibase 사용하는 경우
1. `jdbc-drivers/` 폴더에 해당 `.jar` 파일을 배치
2. 개발 환경 시작
3. 웹 인터페이스에서 Informix/Altibase 서버 추가 가능

## 🏢 데이터솔루션부 프로젝트

이 프로젝트는 데이터솔루션부에서 데이터 동기화 및 마이그레이션 작업을 효율적으로 수행하기 위해 개발되었습니다.

### 주요 기능
- 🔄 **다중 데이터베이스 지원**: PostgreSQL, Informix, Altibase
- 📊 **데이터 동기화**: 다양한 데이터베이스 간 데이터 이동
- 🛠️ **웹 인터페이스**: 사용자 친화적인 관리 도구
- 📈 **모니터링**: 실시간 동기화 상태 확인
- 🔒 **보안**: 안전한 데이터 전송 및 접근 제어 