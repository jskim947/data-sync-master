# 💻 코딩 표준 규칙

## 🎯 코딩 원칙

### 1. 가독성 우선
- 명확하고 이해하기 쉬운 코드
- 적절한 들여쓰기와 공백
- 의미있는 변수명과 함수명

### 2. 일관성 유지
- 프로젝트 전체에서 동일한 스타일
- 팀원 간 코드 스타일 통일
- 기존 코드와의 일관성

### 3. 유지보수성
- 모듈화된 구조
- 재사용 가능한 코드
- 확장 가능한 설계

## 📝 Python 코딩 표준

### 1. 명명 규칙

#### 변수명
```python
# snake_case 사용
user_name = "John"
database_connection = None
is_valid = True

# 상수는 UPPER_CASE
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30
```

#### 함수명
```python
# snake_case 사용
def get_user_info():
    pass

def connect_database():
    pass

def validate_input():
    pass
```

#### 클래스명
```python
# PascalCase 사용
class DatabaseConnection:
    pass

class UserManager:
    pass

class ConfigManager:
    pass
```

#### 모듈명
```python
# snake_case 사용
import db_connection
import user_manager
import config_manager
```

### 2. 들여쓰기 및 공백

#### 들여쓰기
```python
# 4칸 공백 사용 (탭 금지)
def long_function_name(
    parameter1,
    parameter2,
    parameter3
):
    print("Proper indentation")
```

#### 공백 규칙
```python
# 연산자 주변 공백
x = 1 + 2
y = (a + b) * (c - d)

# 쉼표 뒤 공백
my_list = [1, 2, 3, 4]
my_dict = {'a': 1, 'b': 2, 'c': 3}

# 함수 호출 시 공백 없음
function_call(param1, param2)
```

### 3. 주석 규칙

#### 문서화 주석 (Docstring)
```python
def calculate_total(items, tax_rate=0.1):
    """
    상품 목록의 총액을 계산합니다.
    
    Args:
        items (list): 상품 목록
        tax_rate (float): 세율 (기본값: 0.1)
    
    Returns:
        float: 세금 포함 총액
    
    Raises:
        ValueError: items가 비어있거나 tax_rate가 음수일 때
    """
    if not items:
        raise ValueError("상품 목록이 비어있습니다.")
    
    if tax_rate < 0:
        raise ValueError("세율은 음수일 수 없습니다.")
    
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
```

#### 인라인 주석
```python
# 복잡한 로직에 대한 설명
result = complex_calculation()  # O(n^2) 시간 복잡도

# TODO: 향후 개선 예정
# FIXME: 버그 수정 필요
# NOTE: 특별한 경우 처리
```

### 4. 함수 및 클래스 규칙

#### 함수 길이
- 함수는 20줄 이내로 작성
- 복잡한 함수는 여러 개로 분리

#### 매개변수
```python
# 기본값이 있는 매개변수는 뒤에 배치
def create_user(name, email, age=18, is_active=True):
    pass

# 가변 인자 사용
def process_items(*args, **kwargs):
    pass
```

#### 클래스 구조
```python
class DatabaseManager:
    """데이터베이스 연결 및 관리 클래스"""
    
    def __init__(self, connection_string):
        """초기화"""
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self):
        """데이터베이스 연결"""
        pass
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        pass
    
    def execute_query(self, query):
        """쿼리 실행"""
        pass
```

## 🔧 코드 품질 규칙

### 1. 에러 처리

#### 예외 처리
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"값 오류: {e}")
    raise
except ConnectionError as e:
    logger.error(f"연결 오류: {e}")
    # 재시도 로직
    retry_connection()
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
    raise
```

#### 사용자 정의 예외
```python
class DatabaseConnectionError(Exception):
    """데이터베이스 연결 오류"""
    pass

class ValidationError(Exception):
    """데이터 검증 오류"""
    pass
```

### 2. 로깅 규칙

#### 로그 레벨 사용
```python
import logging

logger = logging.getLogger(__name__)

# 디버그 정보
logger.debug("디버그 정보")

# 일반 정보
logger.info("작업 완료")

# 경고
logger.warning("주의사항")

# 오류
logger.error("오류 발생")

# 치명적 오류
logger.critical("치명적 오류")
```

### 3. 타입 힌트 사용

#### 기본 타입 힌트
```python
from typing import List, Dict, Optional, Union

def process_users(users: List[Dict[str, str]]) -> List[str]:
    """사용자 목록을 처리하여 이름 목록 반환"""
    return [user['name'] for user in users]

def get_user_by_id(user_id: int) -> Optional[Dict[str, str]]:
    """사용자 ID로 사용자 정보 조회"""
    pass

def calculate_total(price: Union[int, float], quantity: int) -> float:
    """총액 계산"""
    return float(price) * quantity
```

## 📁 파일 구조 규칙

### 1. 파일 시작 부분
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 설명

이 파일은 데이터베이스 연결을 관리합니다.
"""

import os
import sys
from typing import Optional, Dict, List

# 상수 정의
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# 전역 변수 (최소화)
logger = logging.getLogger(__name__)
```

### 2. import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from typing import List, Dict

# 2. 서드파티 라이브러리
import requests
import pandas as pd

# 3. 로컬 애플리케이션/라이브러리
from .models import User
from .utils import helper_function
```

## 🚫 금지사항

### 1. 코딩 스타일
- 탭 문자 사용 금지
- 80자 초과 라인 길이
- 의미없는 변수명 (a, b, x, y)
- 매직 넘버 사용

### 2. 성능 관련
- 무한 루프
- 메모리 누수
- 비효율적인 알고리즘
- 불필요한 중복 코드

### 3. 보안 관련
- 하드코딩된 비밀번호
- SQL 인젝션 취약점
- 입력값 검증 누락
- 민감한 정보 로깅

## ✅ 코드 리뷰 체크리스트

### 기능성
- [ ] 요구사항 충족
- [ ] 에러 처리 완료
- [ ] 경계값 테스트
- [ ] 예외 상황 처리

### 가독성
- [ ] 명확한 변수명
- [ ] 적절한 주석
- [ ] 일관된 들여쓰기
- [ ] 함수 길이 적절

### 성능
- [ ] 효율적인 알고리즘
- [ ] 불필요한 연산 제거
- [ ] 메모리 사용량 최적화
- [ ] 데이터베이스 쿼리 최적화

### 보안
- [ ] 입력값 검증
- [ ] SQL 인젝션 방지
- [ ] 민감한 정보 보호
- [ ] 접근 권한 확인

## 🔧 도구 및 설정

### 1. 코드 포맷터
```bash
# Black 포맷터 사용
black --line-length=88 src/

# isort로 import 정렬
isort src/
```

### 2. 린터 설정
```ini
# .flake8 설정
[flake8]
max-line-length = 88
exclude = .git,__pycache__,build,dist
ignore = E203, W503
```

### 3. IDE 설정
```json
// VS Code settings.json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.rulers": [88],
    "editor.tabSize": 4
}
```

## 📚 참고 자료

- [PEP 8 - Python 코딩 스타일 가이드](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black 코드 포맷터](https://black.readthedocs.io/) 