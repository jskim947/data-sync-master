# 🔄 깃허브 동기화 가이드

SSH 설정 파일들을 깃허브에 동기화하는 방법입니다.

## 🚀 서버에서 Git 커밋 및 푸시

### 1단계: 변경사항 확인
```bash
git status
```

### 2단계: 파일 추가
```bash
git add .
```

### 3단계: 커밋
```bash
git commit -m "SSH 자동 설정 파일 추가

- setup-ssh-config.bat: SSH 키 자동 사용 설정
- add-client-key.bat: 클라이언트 SSH 키 서버 등록
- client-ssh-setup.bat: 클라이언트 SSH 키 생성
- update-server-keys.bat: 서버 SSH 키 업데이트
- SSH_AUTO_CONFIG.md: SSH 자동 설정 가이드
- manual-ssh-setup.md: 수동 SSH 설정 가이드
- quick-ssh-setup.bat: 빠른 SSH 서버 설정
- install-ssh-server.bat: SSH 서버 설치
- simple-remote-dev.bat: 간단한 원격 개발 환경
- SIMPLE_REMOTE_DEV_GUIDE.md: 간단한 원격 개발 가이드"
```

### 4단계: 푸시
```bash
git push origin main
```

## 💻 클라이언트에서 실행

### 1단계: 최신 코드 가져오기
```bash
git pull origin main
```

### 2단계: SSH 키 생성 (아직 안 했다면)
```bash
# 기존 키 삭제
del %USERPROFILE%\.ssh\id_rsa_data_sync*

# 새 키 생성
ssh-keygen -t rsa -b 4096 -C "data-sync-master@local" -f %USERPROFILE%\.ssh\id_rsa_data_sync -N ""

# 공개키 확인
type %USERPROFILE%\.ssh\id_rsa_data_sync.pub
```

### 3단계: SSH 자동 설정
```bash
# SSH 키 자동 사용 설정
.\setup-ssh-config.bat
```

### 4단계: 서버에 공개키 등록
생성된 공개키를 서버에 알려주세요. 서버에서 다음을 실행합니다:
```bash
.\add-client-key.bat
```

## 📋 클라이언트 실행 순서

1. **프로젝트 클론** (아직 안 했다면):
   ```bash
   git clone https://github.com/jskim947/data-sync-master.git
   cd data-sync-master
   ```

2. **최신 코드 가져오기**:
   ```bash
   git pull origin main
   ```

3. **SSH 키 생성**:
   ```bash
   del %USERPROFILE%\.ssh\id_rsa_data_sync*
   ssh-keygen -t rsa -b 4096 -C "data-sync-master@local" -f %USERPROFILE%\.ssh\id_rsa_data_sync -N ""
   type %USERPROFILE%\.ssh\id_rsa_data_sync.pub
   ```

4. **SSH 자동 설정**:
   ```bash
   .\setup-ssh-config.bat
   ```

5. **공개키를 서버에 전달**:
   - 생성된 공개키를 복사해서 서버에 알려주기
   - 서버에서 `.\add-client-key.bat` 실행

6. **접속 테스트**:
   ```bash
   ssh 10.150.2.150
   ```

## 🎯 VS Code Remote-SSH 설정

1. VS Code에서 Remote-SSH 확장 설치
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. `10.150.2.150` 입력
4. 자동으로 키 인증 사용

## 📁 생성된 파일들

### SSH 설정 파일들:
- `setup-ssh-config.bat` - SSH 키 자동 사용 설정
- `add-client-key.bat` - 클라이언트 SSH 키 서버 등록
- `client-ssh-setup.bat` - 클라이언트 SSH 키 생성
- `update-server-keys.bat` - 서버 SSH 키 업데이트

### 가이드 문서들:
- `SSH_AUTO_CONFIG.md` - SSH 자동 설정 가이드
- `manual-ssh-setup.md` - 수동 SSH 설정 가이드
- `SIMPLE_REMOTE_DEV_GUIDE.md` - 간단한 원격 개발 가이드

### 개발 환경 파일들:
- `simple-remote-dev.bat` - 간단한 원격 개발 환경
- `quick-ssh-setup.bat` - 빠른 SSH 서버 설정
- `install-ssh-server.bat` - SSH 서버 설치

## 🚨 주의사항

1. **개인키 보안**: `id_rsa_data_sync` 파일은 절대 공유하지 마세요
2. **공개키만 공유**: `id_rsa_data_sync.pub` 파일만 서버에 등록
3. **파일 권한**: SSH 파일들은 적절한 권한으로 설정되어야 합니다

## 📞 지원

문제가 발생하면:
1. SSH 디버그 모드: `ssh -v 10.150.2.150`
2. 설정 파일 확인: `type %USERPROFILE%\.ssh\config`
3. 키 상태 확인: `ssh-add -l` 