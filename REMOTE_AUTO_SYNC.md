# 🔄 원격 자동 동기화 가이드

원격 서버(10.150.2.150:5000)에서 실행 중인 애플리케이션에 코드 변경사항을 자동으로 반영하는 방법들입니다.

## 🚀 방법 1: 볼륨 마운트 방식 (원격 서버에서 직접 수정)

### 설정
1. **원격 서버에서** 수정된 `docker-compose.remote-dev.yml` 사용:
```bash
docker-compose -f docker-compose.remote-dev.yml down
docker-compose -f docker-compose.remote-dev.yml up --build -d
```

### 사용법
- **원격 서버에서 직접 파일 수정** → **즉시 반영**
- Flask 개발 모드로 실행되어 자동 리로드
- 파일 저장 시 1-2초 내에 반영

### 장점
- ✅ 가장 빠른 반영 속도
- ✅ 실시간 개발 가능
- ✅ 별도 설정 불필요

### 단점
- ❌ 로컬에서 수정하면 반영되지 않음
- ❌ 원격 서버에서 직접 편집 필요

## 🔄 방법 2: Git 기반 자동 동기화 (로컬에서 수정 시 권장)

### 설정
1. **원격 서버에서** 자동 감지 스크립트 실행:
```bash
chmod +x watch-and-restart.sh
./watch-and-restart.sh
```

### 사용법
1. **로컬에서 코드 수정**
2. **Git 커밋 및 푸시**:
```bash
git add .
git commit -m "코드 수정"
git push origin main
```
3. **원격 서버에서 자동 감지 및 재시작**

### 장점
- ✅ 로컬에서 수정 가능
- ✅ 버전 관리와 함께 안전한 배포
- ✅ 여러 개발자 동시 작업 가능
- ✅ 롤백 가능

### 단점
- ❌ Git 작업 필요
- ❌ 약간의 지연 시간

## 🖥️ 방법 3: VS Code Remote Development (가장 편리)

### 설정
1. **VS Code에서** Remote-SSH 확장 설치
2. **원격 서버 연결**:
   - `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
   - `jskim947@10.150.2.150` 입력

### 사용법
- **VS Code에서 직접 원격 파일 편집**
- **저장 시 즉시 반영**
- **로컬 개발 환경과 동일한 경험**

### 장점
- ✅ 로컬과 동일한 개발 환경
- ✅ 실시간 편집 및 디버깅
- ✅ 확장 기능 사용 가능
- ✅ 로컬에서 편집하는 것처럼 사용

### 단점
- ❌ VS Code Remote-SSH 설정 필요
- ❌ 네트워크 연결 필요

## 🔧 방법 4: 수동 동기화

### Windows에서
```bash
# 로컬에서
sync-to-remote.bat
```

### Linux/Mac에서
```bash
# rsync 사용
rsync -avz --exclude='.git' --exclude='__pycache__' ./ user@10.150.2.150:/path/to/data-sync-master/
```

## 📋 권장 워크플로우

### 로컬에서 수정할 때 (권장 순서)

1. **VS Code Remote Development** (가장 편리)
2. **Git 기반 자동 동기화** (안전하고 버전 관리)
3. **수동 동기화** (간단한 수정)

### 원격 서버에서 직접 수정할 때

1. **볼륨 마운트 방식** (가장 빠름)
2. **SSH로 직접 접속** (터미널 편집)

### 빠른 시작

**로컬에서 수정하는 가장 간단한 방법:**
1. VS Code에서 Remote-SSH로 `jskim947@10.150.2.150` 연결
2. 원격 파일을 로컬처럼 편집
3. 저장 시 즉시 반영

## 🛠️ 문제 해결

### 자동 반영이 안 될 때
1. **Flask 개발 모드 확인**: `FLASK_DEBUG=1`
2. **볼륨 마운트 확인**: `docker-compose ps`
3. **파일 권한 확인**: 원격 서버 파일 권한
4. **네트워크 연결 확인**: SSH 연결 상태

### 성능 최적화
1. **불필요한 파일 제외**: `.gitignore` 설정
2. **캐시 활용**: 브라우저 캐시 설정
3. **리소스 모니터링**: Docker 리소스 사용량 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 원격 서버 로그: `docker-compose -f docker-compose.remote-dev.yml logs web`
2. 네트워크 연결: `ping 10.150.2.150`
3. SSH 연결: `ssh jskim947@10.150.2.150` 