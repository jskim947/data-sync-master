"""
Database Connection Test Module

이 모듈은 Informix, Altibase, PostgreSQL 데이터베이스에 연결하여 쿼리를 실행하는 기능을 제공합니다.
"""

# 원래 db_query.py의 함수들을 직접 import
from .db_query import get_server_config, connect_informix, connect_altibase, connect_postgresql, execute_query

__all__ = ['get_server_config', 'connect_informix', 'connect_altibase', 'connect_postgresql', 'execute_query']
__version__ = '1.0.0' 