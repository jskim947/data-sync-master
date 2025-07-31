# 📁 프로젝트 구조 규칙

## 🎯 디렉토리 구조 원칙

### 1. 목적별 분리
- **src/**: 소스 코드 (핵심 애플리케이션)
- **docker/**: Docker 관련 설정
- **scripts/**: 실행 스크립트
- **config/**: 설정 파일
- **docs/**: 문서
- **tools/**: 유틸리티 및 도구

### 2. 환경별 분리
- **dev/**: 개발 환경
- **prod/**: 운영 환경

## 📋 파일 명명 규칙

### Python 파일
- **snake_case** 사용: `app.py`, `db_connection.py`
- 클래스는 **PascalCase**: `DatabaseConnection`
- 함수는 **snake_case**: `connect_database()`

### 설정 파일
- **kebab-case** 사용: `docker-compose.dev.yml`
- 환경별 접미사: `.dev`, `.prod`

### 스크립트 파일
- **kebab-case** 사용: `start-dev.bat`
- 목적별 접두사: `start-`, `build-`, `deploy-`

## 🔧 코드 구조 규칙

### 1. 모듈화
```
app.py              # 메인 애플리케이션
├── routes/         # 라우트 정의
├── models/         # 데이터 모델
├── services/       # 비즈니스 로직
└── utils/          # 유틸리티 함수
```

### 2. 설정 분리
```
config/
├── env.dev         # 개발 환경변수
├── env.prod        # 운영 환경변수
└── database/       # 데이터베이스 설정
```

### 3. Docker 구조
```
docker/
├── Dockerfile.dev      # 개발용 이미지
├── Dockerfile.prod     # 운영용 이미지
├── docker-compose.dev.yml
└── docker-compose.prod.yml
```

## 📝 문서화 규칙

### 1. README 파일
- 프로젝트 루트에 `README.md`
- 각 디렉토리에 `README.md` (필요시)

### 2. 문서 구조
```
docs/
├── DEVELOPMENT.md      # 개발 가이드
├── DEPLOYMENT.md       # 배포 가이드
├── API.md             # API 문서
└── TROUBLESHOOTING.md # 문제 해결
```

## 🚫 금지사항

### 1. 파일 위치
- 루트에 설정 파일 직접 배치 금지
- 루트에 실행 파일 직접 배치 금지
- 루트에 문서 파일 직접 배치 금지

### 2. 명명 규칙
- 공백 포함 파일명 금지
- 특수문자 사용 금지 (하이픈, 언더스코어 제외)
- 대소문자 혼용 금지

## ✅ 검증 체크리스트

### 프로젝트 구조
- [ ] 목적별 디렉토리 분리
- [ ] 환경별 설정 분리
- [ ] 명명 규칙 준수
- [ ] 문서화 완료

### 코드 품질
- [ ] 모듈화 구조
- [ ] 설정 분리
- [ ] 의존성 관리
- [ ] 에러 처리

## 🔄 유지보수 규칙

### 1. 정기 점검
- 월 1회 프로젝트 구조 검토
- 분기별 문서 업데이트
- 연 1회 불필요한 파일 정리

### 2. 변경 관리
- 구조 변경 시 문서 업데이트
- 팀원 간 변경사항 공유
- 버전 관리 시스템 활용 