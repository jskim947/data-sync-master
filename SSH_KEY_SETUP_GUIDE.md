# 🔑 SSH 키 설정 가이드

클라이언트에서 서버로 SSH 키 인증을 설정하는 방법입니다.

## 🖥️ 서버 설정 (현재 컴퓨터)

### 1단계: SSH 서버 설치 및 시작

**관리자 권한으로 실행**:
```bash
# SSH 서버 설치
dism /online /add-capability /capabilityname:OpenSSH.Server~~~~0.0.1.0

# SSH 서버 시작
net start sshd

# 자동 시작 설정
sc config sshd start=auto

# 방화벽 규칙 추가
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=TCP localport=22
```

또는 `setup-ssh-server.bat` 파일을 **관리자 권한으로 실행**

### 2단계: SSH 키 설정

**일반 사용자 권한으로 실행**:
```bash
# SSH 키 설정 스크립트 실행
setup-server-ssh-keys.bat
```

또는 수동으로 설정:
```bash
# SSH 디렉토리 생성
mkdir %USERPROFILE%\.ssh

# authorized_keys 파일에 클라이언트 공개키 추가
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2/tz26LfVGcosmlUhnTzmi/vrVFjykl6+PkaPPq3xxb0wePjlUjnXdv8Zl97NbPUcXnCOz7eEE/2NVGshnnuTrhkoh6xPSQKIRGxxINrFPCF8x1lx3bIQVUQb+dGNTQ51P6UFw4hQJhcVmLilOnomROEgr2+XyY750usnaGpGrPW0vIIuvuDf+qDkbxdDrLmBw0mibMUspOlLdmwAUwcDBbCbB/nfPvrPNcYymdaf+Ug9huEfKxqHLf+NKUkbM/d4NcrPKj9GHyCM0hmpM3VP2Z3OQHiW195Le1T/JW8+LWf1TZlfjN5xnN2C52fkR5sZ/B11uccIRNuSz+/mj+AtULm8eT3FM6jQitySks1jfeH/+Gk/00xflXCCr8zOR/KSS3AXKekRQfQnzrVtyHiCsxCnklLoZu66w+zhYYHuV68gCMR6ilTEpl7CQvto1wkWeNmuVZUGiVcNJohBBpd5Lk9Y2tljcJ3EPQZ3pmfZrBjv9e0hPyHSLjbXaZKmHOQpuIkNsEiZ6RPEJ1PhQ3rBonxxey+ZovfL+M3Rv84zBlVfkn45cwhnWKKwDQ5ZlM30RyS2W4cM/LHc9rJYnwQgzCHhNCUfJeIR+onJCndu01dCqv72DJIeI+8tKgBtcRS2uh0GCQNkfLgxOfkG4/yhN+pP+QFmbfQGJxsk6ya8fQ== data-sync-manager@local >> %USERPROFILE%\.ssh\authorized_keys

# 파일 권한 설정
icacls %USERPROFILE%\.ssh /inheritance:r
icacls %USERPROFILE%\.ssh /grant:r %USERNAME%:(F)
icacls %USERPROFILE%\.ssh\authorized_keys /inheritance:r
icacls %USERPROFILE%\.ssh\authorized_keys /grant:r %USERNAME%:(F)
```

## 💻 클라이언트 설정 (다른 컴퓨터)

### 1단계: SSH 키 생성

**클라이언트 컴퓨터에서 실행**:
```bash
# SSH 키 설정 스크립트 실행
setup-ssh-keys.bat
```

또는 수동으로 설정:
```bash
# SSH 디렉토리 생성
mkdir %USERPROFILE%\.ssh

# SSH 키 생성
ssh-keygen -t rsa -b 4096 -f %USERPROFILE%\.ssh\id_rsa -N ""

# 공개키 내용 확인 (서버에 등록해야 함)
type %USERPROFILE%\.ssh\id_rsa.pub
```

### 2단계: 서버에 공개키 등록

생성된 공개키를 서버의 `authorized_keys` 파일에 추가해야 합니다.

## 🔗 접속 테스트

### 터미널에서 접속:
```bash
# 클라이언트에서
ssh 사용자명@172.27.64.1
```

### VS Code Remote-SSH 설정:
1. VS Code에서 Remote-SSH 확장 설치
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. `사용자명@172.27.64.1` 입력
4. 비밀번호 없이 자동 연결됨

## 📋 설정 확인

### 서버에서 확인:
```bash
# SSH 서비스 상태
sc query sshd

# authorized_keys 파일 확인
type %USERPROFILE%\.ssh\authorized_keys

# SSH 디렉토리 권한 확인
icacls %USERPROFILE%\.ssh
```

### 클라이언트에서 확인:
```bash
# SSH 키 파일 확인
dir %USERPROFILE%\.ssh

# 공개키 내용 확인
type %USERPROFILE%\.ssh\id_rsa.pub
```

## 🛠️ 문제 해결

### SSH 연결이 안 될 때:
1. **SSH 서비스 확인**: `sc query sshd`
2. **방화벽 확인**: Windows 방화벽에서 포트 22 허용
3. **파일 권한 확인**: `.ssh` 디렉토리와 `authorized_keys` 파일 권한
4. **공개키 확인**: 서버의 `authorized_keys`에 클라이언트 공개키가 있는지 확인

### 권한 문제:
1. **관리자 권한**: SSH 서버 설치 시 필요
2. **파일 권한**: `.ssh` 디렉토리는 현재 사용자만 접근 가능해야 함

### 키 인증이 안 될 때:
1. **공개키 형식 확인**: 올바른 SSH 공개키 형식인지 확인
2. **파일 위치 확인**: `%USERPROFILE%\.ssh\authorized_keys`
3. **SSH 서버 로그 확인**: 이벤트 뷰어에서 SSH 관련 로그 확인

## 🔒 보안 권장사항

1. **강력한 키 사용**: 최소 4096비트 RSA 키 사용
2. **키 파일 보호**: 개인키 파일은 절대 공유하지 않음
3. **정기적인 키 교체**: 보안을 위해 정기적으로 키 교체
4. **접속 로그 모니터링**: SSH 접속 로그 정기 확인

## 📞 지원

문제가 발생하면:
1. SSH 서비스 로그 확인
2. 네트워크 연결 테스트: `telnet 172.27.64.1 22`
3. SSH 키 파일 권한 확인
4. 방화벽 설정 확인 