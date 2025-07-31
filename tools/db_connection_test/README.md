# 데이터베이스 쿼리 실행기

여러 데이터베이스(PostgreSQL, Informix, Altibase)에 연결하여 쿼리를 실행할 수 있는 Python 도구입니다.

## 기능

- **다중 데이터베이스 지원**: PostgreSQL, Informix, Altibase
- **인터랙티브 모드**: 사용자 친화적 인터페이스
- **명령행 모드**: 자동화 스크립트에서 사용 가능
- **모듈화**: 다른 프로젝트에서 import하여 사용 가능
- **데이터 타입 변환**: Java 객체를 Python 객체로 자동 변환

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. JDBC 드라이버 준비

- `Altibase.jar`: Altibase JDBC 드라이버
- `ifxjdbc.jar`: Informix JDBC 드라이버

### 3. 설정 파일 생성

`db_servers.ini` 파일을 생성하고 데이터베이스 연결 정보를 설정하세요:

```ini
[altibase_server]
type = altibase
host = 190.1.100.213
port = 20300
database = infomax
user = infomax
password = infomax!

[FS1]
type = postgresql
host = 190.1.100.101
port = 5432
database = infomax
user = postgres
password = infomax!

[m22]
type = informix
host = localhost
port = 8586
database = infomax
user = your_username
password = your_password
```

## 사용법

### 1. 인터랙티브 모드

```bash
python db_query.py
```

서버를 선택하고 쿼리를 입력하여 실행할 수 있습니다.

### 2. 명령행 모드

```bash
# 서버명과 쿼리를 함께 지정
python db_query.py altibase_server "SELECT COUNT(*) FROM ST1550TB"

# 서버명만 지정하고 쿼리는 입력받기
python db_query.py altibase_server
```

### 3. 모듈로 사용

```python
from db_query import execute_query

# 쿼리 실행
rows, success, error = execute_query('altibase_server', 'SELECT * FROM ST1550TB WHERE ROWNUM <= 10')

if success:
    for row in rows:
        print(row)
else:
    print(f"오류: {error}")
```

## 지원하는 데이터 타입

### PostgreSQL
- 모든 기본 데이터 타입 지원
- `Decimal` → `float` 자동 변환
- `datetime` 객체 지원

### Altibase
- Java 객체를 Python 객체로 자동 변환
- `BigDecimal` → `int`/`float` (정밀도 유지)
- `String` → `str`
- `Integer`/`Long` → `int`

### Informix
- 모든 기본 데이터 타입 지원

## 파일 구조

```
db_connection_test/
├── db_query.py          # 메인 실행 파일
├── db_servers.ini       # 데이터베이스 설정 파일
├── requirements.txt     # Python 의존성
├── Altibase.jar        # Altibase JDBC 드라이버
├── ifxjdbc.jar         # Informix JDBC 드라이버
└── README.md           # 이 파일
```

## 주요 함수

### `execute_query(server_name, query)`
- 서버에 연결하여 쿼리를 실행
- 반환값: `(rows, success, error)`

### `connect_altibase(conf)`
- Altibase 데이터베이스 연결

### `connect_postgresql(conf)`
- PostgreSQL 데이터베이스 연결

### `connect_informix(conf)`
- Informix 데이터베이스 연결

### `convert_java_to_python(value)`
- Java 객체를 Python 객체로 변환

## 예제

### Altibase 쿼리 실행
```python
rows, success, error = execute_query('altibase_server', 'SELECT * FROM ST1550TB WHERE ROWNUM <= 5')
```

### PostgreSQL 쿼리 실행
```python
rows, success, error = execute_query('FS1', 'SELECT * FROM users LIMIT 10')
```

### Informix 쿼리 실행
```python
rows, success, error = execute_query('m22', 'SELECT * FROM customers')
```

## 주의사항

1. **JDBC 드라이버**: Altibase와 Informix 사용 시 해당 JDBC 드라이버가 필요합니다.
2. **Java 환경**: `jaydebeapi` 사용을 위해 Java가 설치되어 있어야 합니다.
3. **네트워크 연결**: 데이터베이스 서버에 네트워크 접근이 가능해야 합니다.
4. **권한**: 데이터베이스 사용자에게 적절한 권한이 필요합니다.

## 문제 해결

### 연결 오류
- 데이터베이스 서버가 실행 중인지 확인
- 네트워크 연결 상태 확인
- 사용자명/비밀번호 확인

### JDBC 드라이버 오류
- JDBC 드라이버 파일이 올바른 위치에 있는지 확인
- 드라이버 버전이 데이터베이스 버전과 호환되는지 확인

### 데이터 타입 변환 오류
- Java 객체 변환 로직이 모든 케이스를 처리하는지 확인
- 필요시 `convert_java_to_python` 함수를 확장 