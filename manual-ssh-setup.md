# 🔧 수동 SSH 서버 설치 가이드

Windows에서 SSH 서버를 수동으로 설치하고 설정하는 방법입니다.

## 🚀 1단계: 관리자 권한으로 PowerShell 실행

1. **Windows 키 + X** → **"Windows PowerShell (관리자)"** 선택
2. 또는 **시작 메뉴** → **"PowerShell"** 검색 → **"관리자 권한으로 실행"**

## 📦 2단계: OpenSSH 서버 설치

관리자 PowerShell에서 다음 명령어 실행:

```powershell
# OpenSSH 서버 기능 설치
dism /online /add-capability /capabilityname:OpenSSH.Server~~~~0.0.1.0

# 설치 확인
Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH*"
```

## 🔧 3단계: SSH 서버 설정

```powershell
# SSH 서버 서비스 시작
Start-Service sshd

# SSH 서버 자동 시작 설정
Set-Service -Name sshd -StartupType 'Automatic'

# SSH 서버 상태 확인
Get-Service sshd
```

## 🛡️ 4단계: 방화벽 설정

```powershell
# SSH 포트(22) 방화벽 규칙 추가
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

## 🔑 5단계: SSH 키 설정

### SSH 디렉토리 생성:
```powershell
# SSH 디렉토리 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force

# authorized_keys 파일 생성
New-Item -ItemType File -Path "$env:USERPROFILE\.ssh\authorized_keys" -Force
```

### 클라이언트 공개키 추가:
```powershell
# authorized_keys 파일에 클라이언트 공개키 추가
Add-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2/tz26LfVGcosmlUhnTzmi/vrVFjykl6+PkaPPq3xxb0wePjlUjnXdv8Zl97NbPUcXnCOz7eEE/2NVGshnnuTrhkoh6xPSQKIRGxxINrFPCF8x1lx3bIQVUQb+dGNTQ51P6UFw4hQJhcVmLilOnomROEgr2+XyY750usnaGpGrPW0vIIuvuDf+qDkbxdDrLmBw0mibMUspOlLdmwAUwcDBbCbB/nfPvrPNcYymdaf+Ug9huEfKxqHLf+NKUkbM/d4NcrPKj9GHyCM0hmpM3VP2Z3OQHiW195Le1T/JW8+LWf1TZlfjN5xnN2C52fkR5sZ/B11uccIRNuSz+/mj+AtULm8eT3FM6jQitySks1jfeH/+Gk/00xflXCCr8zOR/KSS3AXKekRQfQnzrVtyHiCsxCnklLoZu66w+zhYYHuV68gCMR6ilTEpl7CQvto1wkWeNmuVZUGiVcNJohBBpd5Lk9Y2tljcJ3EPQZ3pmfZrBjv9e0hPyHSLjbXaZKmHOQpuIkNsEiZ6RPEJ1PhQ3rBonxxey+ZovfL+M3Rv84zBlVfkn45cwhnWKKwDQ5ZlM30RyS2W4cM/LHc9rJYnwQgzCHhNCUfJeIR+onJCndu01dCqv72DJIeI+8tKgBtcRS2uh0GCQNkfLgxOfkG4/yhN+pP+QFmbfQGJxsk6ya8fQ== data-sync-manager@local"
```

### 파일 권한 설정:
```powershell
# SSH 디렉토리 권한 설정
icacls "$env:USERPROFILE\.ssh" /inheritance:r
icacls "$env:USERPROFILE\.ssh" /grant:r "$env:USERNAME:(F)"

# authorized_keys 파일 권한 설정
icacls "$env:USERPROFILE\.ssh\authorized_keys" /inheritance:r
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant:r "$env:USERNAME:(F)"
```

## 🌐 6단계: IP 주소 확인

```powershell
# IP 주소 확인
ipconfig | findstr "IPv4"
```

## ✅ 7단계: 설정 확인

```powershell
# SSH 서비스 상태 확인
Get-Service sshd

# SSH 포트 확인
netstat -an | findstr :22

# authorized_keys 파일 확인
Get-Content "$env:USERPROFILE\.ssh\authorized_keys"
```

## 🔗 8단계: 접속 테스트

### 클라이언트에서 테스트:
```bash
# 터미널에서
ssh 사용자명@IP주소

# 또는 VS Code Remote-SSH에서
# Host: IP주소
# User: 사용자명
```

## 🛠️ 문제 해결

### SSH 서비스가 시작되지 않을 때:
```powershell
# 서비스 상태 확인
Get-Service sshd

# 서비스 시작
Start-Service sshd

# 서비스 로그 확인
Get-EventLog -LogName System -Source "OpenSSH*" -Newest 10
```

### 방화벽 문제:
```powershell
# 방화벽 규칙 확인
Get-NetFirewallRule -Name sshd

# 방화벽 규칙 다시 추가
Remove-NetFirewallRule -Name sshd -ErrorAction SilentlyContinue
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### 권한 문제:
```powershell
# SSH 디렉토리 권한 재설정
icacls "$env:USERPROFILE\.ssh" /reset
icacls "$env:USERPROFILE\.ssh" /inheritance:r
icacls "$env:USERPROFILE\.ssh" /grant:r "$env:USERNAME:(F)"
```

## 📋 완료 체크리스트

- [ ] 관리자 권한으로 PowerShell 실행
- [ ] OpenSSH 서버 설치
- [ ] SSH 서비스 시작 및 자동 시작 설정
- [ ] 방화벽 규칙 추가
- [ ] SSH 디렉토리 및 authorized_keys 파일 생성
- [ ] 클라이언트 공개키 추가
- [ ] 파일 권한 설정
- [ ] IP 주소 확인
- [ ] 접속 테스트

## 🎯 접속 정보

설정 완료 후:
- **IP 주소**: 위에서 확인된 IP
- **포트**: 22
- **사용자명**: 현재 Windows 사용자명
- **인증 방식**: SSH 키 (비밀번호 없음)

## 💻 VS Code Remote-SSH 설정

1. VS Code에서 Remote-SSH 확장 설치
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. `사용자명@IP주소` 입력
4. 비밀번호 없이 자동 연결 