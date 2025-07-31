# 🧹 프로젝트 정리 및 개발/운영 환경 분리 계획

## 📋 현재 상황 분석

### 🔴 삭제 대상 파일들 (SSH 관련, 중복, 불필요)
- SSH 관련 파일들 (20개+)
- 중복된 시작 스크립트들
- 테스트용 임시 파일들
- 불필요한 가이드 문서들

### 🟢 유지할 핵심 파일들
- `app.py` - 메인 애플리케이션
- `requirements.txt` - Python 의존성
- `Dockerfile` - 기본 Docker 이미지
- `docker-compose.yml` - 기본 설정
- `templates/` - 웹 템플릿
- `jdbc-drivers/` - 데이터베이스 드라이버
- `db_connection_test/` - DB 연결 테스트

## 🎯 제안하는 환경 분리 구조

### 1. 개발 환경 (Development)
```
📁 개발 환경
├── 📄 docker-compose.dev.yml     # 개발용 Docker Compose
├── 📄 Dockerfile.dev             # 개발용 Dockerfile (볼륨 마운트)
├── 📄 start-dev.bat              # 개발 환경 시작
├── 📄 auto-sync-system.bat       # Git 자동 동기화
└── 📄 .env.dev                   # 개발용 환경변수
```

**특징:**
- ✅ 소스 코드 볼륨 마운트 (실시간 반영)
- ✅ 디버그 모드 활성화
- ✅ Git 자동 동기화
- ✅ 핫 리로드 지원

### 2. 운영 환경 (Production)
```
📁 운영 환경
├── 📄 docker-compose.prod.yml    # 운영용 Docker Compose
├── 📄 Dockerfile.prod            # 운영용 Dockerfile (최적화)
├── 📄 start-prod.bat             # 운영 환경 시작
├── 📄 build-prod.bat             # 운영 이미지 빌드
└── 📄 .env.prod                  # 운영용 환경변수
```

**특징:**
- ✅ 최적화된 Docker 이미지
- ✅ 보안 강화
- ✅ 성능 최적화
- ✅ 로그 관리

## 🚀 구현 계획

### Phase 1: 프로젝트 정리
1. **불필요한 파일 삭제**
2. **중복 파일 통합**
3. **디렉토리 구조 정리**

### Phase 2: 개발 환경 구축
1. **개발용 Docker 설정**
2. **자동 동기화 시스템**
3. **디버그 환경 구성**

### Phase 3: 운영 환경 구축
1. **운영용 Docker 설정**
2. **이미지 빌드 시스템**
3. **배포 스크립트**

### Phase 4: 통합 관리
1. **환경별 스크립트**
2. **모니터링 시스템**
3. **백업/복구 시스템**

## 📁 제안하는 최종 디렉토리 구조

```
data-sync-master/
├── 📁 src/                          # 소스 코드
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
├── 📁 docker/                       # Docker 설정
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── 📁 scripts/                      # 스크립트
│   ├── dev/
│   │   ├── start-dev.bat
│   │   └── auto-sync.bat
│   └── prod/
│       ├── start-prod.bat
│       └── build-prod.bat
├── 📁 config/                       # 설정 파일
│   ├── .env.dev
│   ├── .env.prod
│   └── database/
├── 📁 docs/                         # 문서
│   ├── README.md
│   ├── DEVELOPMENT.md
│   └── DEPLOYMENT.md
└── 📁 tools/                        # 도구
    ├── jdbc-drivers/
    └── db_connection_test/
```

## 🔄 개발 워크플로우

### 개발자 워크플로우:
1. **로컬 개발**: 코드 수정
2. **Git 커밋**: `git add . && git commit -m "수정사항"`
3. **Git 푸시**: `git push origin main`
4. **자동 배포**: 서버에서 자동 감지 및 반영

### 운영 배포 워크플로우:
1. **코드 준비**: 개발 완료된 코드
2. **이미지 빌드**: `.\scripts\prod\build-prod.bat`
3. **운영 배포**: `.\scripts\prod\start-prod.bat`
4. **모니터링**: 로그 및 성능 확인

## 🛠️ 구현할 스크립트들

### 개발 환경:
- `start-dev.bat` - 개발 환경 시작
- `auto-sync.bat` - Git 자동 동기화
- `dev-logs.bat` - 개발 로그 확인

### 운영 환경:
- `build-prod.bat` - 운영 이미지 빌드
- `start-prod.bat` - 운영 환경 시작
- `prod-logs.bat` - 운영 로그 확인
- `backup-prod.bat` - 운영 데이터 백업

### 공통:
- `cleanup.bat` - 프로젝트 정리
- `status.bat` - 환경 상태 확인
- `restart.bat` - 환경 재시작

## 💡 추가 제안사항

### 1. 환경별 설정 분리
- 개발: 디버그 모드, 상세 로그
- 운영: 최적화, 보안 강화

### 2. 데이터베이스 관리
- 개발: 로컬/테스트 DB
- 운영: 전용 DB 서버

### 3. 모니터링 시스템
- 개발: 간단한 로그
- 운영: 상세 모니터링

### 4. 백업 시스템
- 개발: 코드 백업
- 운영: 데이터 + 코드 백업

## 🎯 다음 단계

1. **프로젝트 정리 실행**
2. **개발 환경 구축**
3. **운영 환경 구축**
4. **테스트 및 검증**

이 계획으로 진행하시겠습니까? 어떤 부분부터 시작하고 싶으신지 알려주세요! 🚀 