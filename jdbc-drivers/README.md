# JDBC Drivers

이 폴더에는 데이터베이스 연결에 필요한 JDBC 드라이버 파일들을 저장합니다.

## 📁 필요한 파일들

### Informix JDBC Driver
- **파일명**: `ifxjdbc.jar`
- **다운로드**: IBM Informix JDBC Driver
- **용량**: 약 2-3MB

### Altibase JDBC Driver  
- **파일명**: `Altibase.jar`
- **다운로드**: Altibase 공식 사이트
- **용량**: 약 1-2MB

## 📥 다운로드 방법

### Informix JDBC Driver
1. IBM Informix 공식 사이트 방문
2. JDBC Driver 다운로드
3. `ifxjdbc.jar` 파일을 이 폴더에 복사

### Altibase JDBC Driver
1. Altibase 공식 사이트 방문  
2. JDBC Driver 다운로드
3. `Altibase.jar` 파일을 이 폴더에 복사

## 🚀 사용법

Docker 컨테이너에서 자동으로 이 폴더의 JDBC 드라이버를 사용합니다.

## ⚠️ 주의사항

- 이 파일들은 라이선스가 있으므로 GitHub에 업로드하지 마세요
- `.gitignore`에 `*.jar`가 포함되어 있습니다
- 프로젝트 배포 시 별도로 JDBC 드라이버를 제공해야 합니다 