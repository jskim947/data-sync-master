# 🔑 SSH 키 자동 사용 설정 가이드

SSH가 자동으로 키 인증을 사용하도록 설정하는 방법입니다.

## 🚀 빠른 설정

### 클라이언트에서 실행:
```bash
# SSH 자동 설정
.\setup-ssh-config.bat
```

## 📋 설정 내용

### SSH 설정 파일 (`~/.ssh/config`):

```bash
# 특정 호스트 설정
Host 10.150.2.150
    HostName 10.150.2.150
    User infomax
    Port 22
    IdentityFile ~/.ssh/id_rsa_data_sync
    PreferredAuthentications publickey
    PubkeyAuthentication yes
    PasswordAuthentication no
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# 전역 설정 (모든 호스트에 적용)
Host *
    PreferredAuthentications publickey
    PubkeyAuthentication yes
    PasswordAuthentication no
    IdentitiesOnly yes
```

## 🔧 설정 옵션 설명

### 인증 관련:
- `PreferredAuthentications publickey`: 키 인증을 우선 사용
- `PubkeyAuthentication yes`: 키 인증 활성화
- `PasswordAuthentication no`: 비밀번호 인증 비활성화
- `IdentitiesOnly yes`: 지정된 키만 사용

### 보안 관련:
- `StrictHostKeyChecking no`: 호스트 키 확인 건너뛰기
- `UserKnownHostsFile /dev/null`: 알려진 호스트 파일 무시

### 연결 관련:
- `IdentityFile ~/.ssh/id_rsa_data_sync`: 사용할 개인키 파일
- `Port 22`: SSH 포트

## 🧪 테스트 방법

### 1. 간단한 접속 테스트:
```bash
ssh 10.150.2.150
```

### 2. 명령어 실행 테스트:
```bash
ssh 10.150.2.150 "echo 'SSH 키 인증 성공!'"
```

### 3. VS Code Remote-SSH 테스트:
1. VS Code에서 Remote-SSH 확장 설치
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. `10.150.2.150` 입력
4. 자동으로 키 인증 사용

## 🛠️ 문제 해결

### SSH 키가 인식되지 않을 때:
```bash
# SSH 에이전트 시작
eval $(ssh-agent)

# 키 추가
ssh-add ~/.ssh/id_rsa_data_sync

# 키 확인
ssh-add -l
```

### 설정 파일 권한 문제:
```bash
# 권한 재설정
chmod 600 ~/.ssh/config
chmod 700 ~/.ssh
```

### 디버그 모드로 연결 테스트:
```bash
ssh -v 10.150.2.150
```

## 📁 파일 구조

```
~/.ssh/
├── config              # SSH 설정 파일
├── id_rsa_data_sync    # 개인키 (클라이언트)
├── id_rsa_data_sync.pub # 공개키 (클라이언트)
└── authorized_keys     # 인증키 (서버)
```

## 🎯 사용법

### 일반 접속:
```bash
ssh 10.150.2.150
```

### 파일 전송:
```bash
scp local_file.txt 10.150.2.150:/remote/path/
```

### 원격 명령 실행:
```bash
ssh 10.150.2.150 "ls -la"
```

## 🔒 보안 주의사항

1. **개인키 보호**: 개인키 파일은 절대 공유하지 마세요
2. **권한 설정**: SSH 파일들은 적절한 권한으로 설정되어야 합니다
3. **정기 업데이트**: SSH 키를 정기적으로 교체하세요

## 📞 지원

문제가 발생하면:
1. SSH 디버그 모드: `ssh -v 10.150.2.150`
2. 설정 파일 확인: `cat ~/.ssh/config`
3. 키 상태 확인: `ssh-add -l` 