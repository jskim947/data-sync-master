# 🔒 보안 가이드 (Security Guide)

## 🚨 중요: GitGuardian 보안 경고 해결

GitGuardian에서 감지된 Generic Password 노출 문제를 해결하기 위한 가이드입니다.

## 📋 수정된 내용

### 1. 하드코딩된 비밀번호 제거
- ✅ `db_connection_test/README.md` - 실제 비밀번호 제거
- ✅ `tools/db_connection_test/README.md` - 실제 비밀번호 제거
- ✅ `docker-compose.yml` - 환경변수 사용
- ✅ `app.py` - 환경변수 사용
- ✅ `config/env.*` - 기본값 변경

### 2. 환경변수 관리
- ✅ `env.example` 파일 생성
- ✅ `.gitignore`에 보안 파일 추가

## 🔧 안전한 비밀번호 설정 방법

### 1. 환경변수 파일 생성
```bash
# 예시 파일을 복사
cp env.example .env

# .env 파일 편집 (실제 비밀번호 입력)
nano .env
```

### 2. 강력한 비밀번호 생성
```bash
# 랜덤 비밀번호 생성 (Linux/Mac)
openssl rand -base64 32

# 또는 Python으로 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Docker 실행 시 환경변수 전달
```bash
# 방법 1: 환경변수 직접 전달
POSTGRES_PASSWORD=your_secure_password docker-compose up -d

# 방법 2: .env 파일 사용
docker-compose --env-file .env up -d
```

## 🛡️ 보안 모범 사례

### 1. 비밀번호 관리
- ❌ **절대 하드코딩하지 마세요**
- ✅ **환경변수 사용**
- ✅ **강력한 비밀번호 사용** (최소 16자, 특수문자 포함)
- ✅ **정기적인 비밀번호 변경**

### 2. Git 보안
- ❌ **민감한 정보를 Git에 커밋하지 마세요**
- ✅ **`.env` 파일은 `.gitignore`에 포함**
- ✅ **예시 파일만 커밋** (`env.example`)
- ✅ **실제 비밀번호는 별도 관리**

### 3. 데이터베이스 보안
- ✅ **최소 권한 원칙 적용**
- ✅ **네트워크 접근 제한**
- ✅ **SSL/TLS 연결 사용**
- ✅ **정기적인 백업**

## 🔍 보안 점검 체크리스트

### 코드 검토
- [ ] 하드코딩된 비밀번호 제거
- [ ] 환경변수 사용
- [ ] 민감한 정보가 Git 히스토리에 남아있지 않음
- [ ] `.gitignore`에 보안 파일 포함

### 환경 설정
- [ ] 강력한 비밀번호 사용
- [ ] 환경변수 파일 생성
- [ ] 프로덕션 환경 분리
- [ ] 접근 권한 제한

### 모니터링
- [ ] GitGuardian 알림 설정
- [ ] 정기적인 보안 스캔
- [ ] 로그 모니터링
- [ ] 접근 로그 검토

## 🚨 긴급 조치 사항

### 1. 즉시 실행
```bash
# 기존 비밀번호 변경
docker-compose down
# .env 파일에서 새 비밀번호 설정
docker-compose up -d
```

### 2. Git 히스토리 정리 (필요시)
```bash
# 민감한 정보가 포함된 커밋 제거
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch 파일명' \
  --prune-empty --tag-name-filter cat -- --all
```

### 3. 데이터베이스 비밀번호 변경
```sql
-- PostgreSQL 비밀번호 변경
ALTER USER postgres PASSWORD 'new_secure_password';
```

## 📞 지원

보안 관련 문의사항이 있으시면:
1. 이슈 생성 시 "Security" 라벨 추가
2. 민감한 정보는 이슈에 직접 포함하지 마세요
3. 보안 관련 코드는 별도 채널로 공유

---

**⚠️ 주의**: 이 가이드를 따라도 100% 보안을 보장할 수는 없습니다. 정기적인 보안 점검과 업데이트가 필요합니다. 