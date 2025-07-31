"""
FS Master Web Application

웹 기반 데이터 마이그레이션 도구
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import os
import sys
import json
import configparser
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
import time
import argparse
import psycopg2
from psycopg2 import OperationalError
import traceback

# db_connection_test import
from db_connection_test import get_server_config, connect_altibase, connect_informix, connect_postgresql, execute_query as db_execute_query

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 시간대 설정 (KST)
KST = timezone(timedelta(hours=9))
app.config['TIMEZONE'] = KST

# 환경변수에서 데이터베이스 설정 읽기 (Docker 환경)
database_url = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 설정
CORS(app)

# 데이터베이스 설정
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 스케줄러 설정 (KST 시간대 사용)
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
scheduler.start()

def get_kst_now():
    """현재 KST 시간 반환"""
    return datetime.now(KST)

def utc_to_kst(utc_time):
    """UTC 시간을 KST로 변환"""
    if utc_time is None:
        return None
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(KST)

def kst_to_utc(kst_time):
    """KST 시간을 UTC로 변환"""
    if kst_time is None:
        return None
    if kst_time.tzinfo is None:
        kst_time = kst_time.replace(tzinfo=KST)
    return kst_time.astimezone(timezone.utc)

def format_kst_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """KST 시간을 포맷팅"""
    if dt is None:
        return '-'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    kst_time = dt.astimezone(KST)
    return kst_time.strftime(format_str)

def format_db_kst_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """DB에 저장된 KST 시간을 포맷팅 (tzinfo가 None인 경우 KST로 가정)"""
    if dt is None:
        return '-'
    if dt.tzinfo is None:
        # DB에 저장된 시간은 이미 KST이므로 tzinfo만 설정
        dt = dt.replace(tzinfo=KST)
    return dt.strftime(format_str)

def parse_cron_expression(cron_expr):
    """Cron 표현식을 사람이 읽기 쉬운 형태로 변환"""
    try:
        parts = cron_expr.split()
        if len(parts) != 5:
            return cron_expr
        
        minute, hour, day, month, weekday = parts
        
        # 요일 매핑
        weekday_names = ['일', '월', '화', '수', '목', '금', '토']
        
        # 분 처리
        if minute == '*':
            minute_desc = '모든 분'
        elif ',' in minute:
            minute_desc = f"{minute.replace(',', ', ')}분"
        elif '-' in minute:
            start, end = minute.split('-')
            minute_desc = f"{start}~{end}분"
        else:
            minute_desc = f"{minute}분"
        
        # 시간 처리
        if hour == '*':
            hour_desc = '모든 시간'
        elif ',' in hour:
            hours = hour.split(',')
            hour_desc = f"{', '.join(hours)}시"
        elif '-' in hour:
            start, end = hour.split('-')
            hour_desc = f"{start}~{end}시"
        else:
            hour_desc = f"{hour}시"
        
        # 일 처리
        if day == '*':
            day_desc = '모든 일'
        elif ',' in day:
            days = day.split(',')
            day_desc = f"{', '.join(days)}일"
        elif '-' in day:
            start, end = day.split('-')
            day_desc = f"{start}~{end}일"
        else:
            day_desc = f"{day}일"
        
        # 월 처리
        if month == '*':
            month_desc = '모든 월'
        elif ',' in month:
            months = month.split(',')
            month_desc = f"{', '.join(months)}월"
        elif '-' in month:
            start, end = month.split('-')
            month_desc = f"{start}~{end}월"
        else:
            month_desc = f"{month}월"
        
        # 요일 처리
        if weekday == '*':
            weekday_desc = '모든 요일'
        elif ',' in weekday:
            weekdays = weekday.split(',')
            weekday_names_list = [weekday_names[int(w)] for w in weekdays]
            weekday_desc = f"{', '.join(weekday_names_list)}요일"
        elif '-' in weekday:
            start, end = weekday.split('-')
            start_name = weekday_names[int(start)]
            end_name = weekday_names[int(end)]
            weekday_desc = f"{start_name}~{end_name}요일"
        else:
            weekday_desc = f"{weekday_names[int(weekday)]}요일"
        
        # 특별한 패턴들
        if cron_expr == '0 0 * * *':
            return '매일 자정 (00:00)'
        elif cron_expr == '0 0 * * 1-5':
            return '월~금 자정'
        elif cron_expr == '0 0 * * 6-0':
            return '토~일 자정'
        elif cron_expr == '0 9 * * 1-5':
            return '월~금 오전 9시'
        elif cron_expr == '0 12 * * 1-5':
            return '월~금 오후 12시'
        elif cron_expr == '0 18 * * 1-5':
            return '월~금 오후 6시'
        elif cron_expr == '20 5 * * 1-5':
            return '월~금 오전 5시 20분'
        elif cron_expr == '20 12 * * 1-5':
            return '월~금 오후 12시 20분'
        elif cron_expr == '0 9,18 * * 1-5':
            return '월~금 9시, 18시'
        elif cron_expr == '0 */6 * * *':
            return '6시간마다'
        elif cron_expr == '0 */12 * * *':
            return '12시간마다'
        elif cron_expr == '0 */24 * * *':
            return '24시간마다'
        
        # 일반적인 패턴
        if minute != '*' and hour != '*' and day == '*' and month == '*' and weekday == '*':
            return f"매일 {hour}시 {minute}분"
        elif minute != '*' and hour != '*' and day == '*' and month == '*' and weekday != '*':
            return f"{weekday_desc} {hour}시 {minute}분"
        elif minute != '*' and hour != '*' and day != '*' and month == '*' and weekday == '*':
            return f"매월 {day}일 {hour}시 {minute}분"
        
        # 복잡한 패턴
        return f"{weekday_desc} {hour_desc} {minute_desc}"
        
    except Exception as e:
        return cron_expr

def test_informix_connection(conf, test_query):
    """Informix 연결 테스트 (별도 함수)"""
    import jaydebeapi
    import os
    
    # 시도할 드라이버 클래스명들 (JAR 파일 분석 결과 기반)
    driver_classes = [
        "com.informix.jdbc.IfxDriver",  # 실제 JAR 파일에 존재하는 클래스
        "com.informix.jdbc.driver.IfxDriver",
        "IfxDriver"
    ]
    
    # 시도할 JAR 파일 경로들 (절대 경로 우선)
    jar_paths = [
        "/app/db_connection_test/ifxjdbc.jar",
        "/app/jdbc-drivers/ifxjdbc.jar",
        "ifxjdbc.jar",
        "./ifxjdbc.jar"
    ]
    
    # JAR 파일 존재 여부 확인
    print("=== Informix JAR 파일 확인 ===")
    for jar in jar_paths:
        if os.path.exists(jar):
            print(f"✅ JAR 파일 존재: {jar}")
        else:
            print(f"❌ JAR 파일 없음: {jar}")
    
    for driver in driver_classes:
        for jar in jar_paths:
            try:
                # 작업 디렉토리를 db_connection_test로 변경
                original_cwd = os.getcwd()
                os.chdir('/app/db_connection_test')
                
                try:
                    print(f"\n=== Informix 연결 시도 ===")
                    print(f"드라이버: {driver}")
                    print(f"JAR 파일: {jar}")
                    print(f"호스트: {conf['host']}:{conf['port']}")
                    print(f"데이터베이스: {conf['database']}")
                    print(f"사용자: {conf['user']}")
                    
                    # 직접 jaydebeapi로 연결 (절대 경로 사용)
                    url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
                    print(f"연결 URL: {url}")
                    
                    # JAR 파일이 실제로 존재하는지 확인
                    if not os.path.exists(jar):
                        print(f"❌ JAR 파일이 존재하지 않음: {jar}")
                        continue
                    
                    print(f"JAR 파일 크기: {os.path.getsize(jar)} bytes")
                    
                    # 연결 시도
                    conn = jaydebeapi.connect(driver, url, [conf['user'], conf['password']], jar)
                    print(f"✅ JDBC 연결 성공")
                    
                    # Java 레벨에서 직접 접근
                    java_conn = conn.jconn
                    java_stmt = java_conn.createStatement()
                    java_stmt.setQueryTimeout(30)
                    
                    print(f"테스트 쿼리 실행: {test_query}")
                    java_result_set = java_stmt.executeQuery(test_query)
                    
                    # 결과 가져오기
                    rows = []
                    while java_result_set.next():
                        meta_data = java_result_set.getMetaData()
                        column_count = meta_data.getColumnCount()
                        
                        row = []
                        for i in range(1, column_count + 1):
                            value = java_result_set.getObject(i)
                            row.append(value)
                        
                        rows.append(tuple(row))
                    
                    # 자원 반납
                    java_result_set.close()
                    java_stmt.close()
                    conn.close()
                    
                    print(f"✅ Informix 연결 성공: {driver}, {jar}")
                    print(f"테스트 결과: {rows}")
                    return rows, True, None
                    
                except Exception as e:
                    print(f"❌ Informix 연결 실패: {driver}, {jar}")
                    print(f"오류 상세: {str(e)}")
                    import traceback
                    print(f"스택 트레이스: {traceback.format_exc()}")
                    continue
                    
                finally:
                    # 작업 디렉토리 복원
                    os.chdir(original_cwd)
                    
            except Exception as e:
                print(f"❌ Informix 연결 시도 실패: {driver}, {jar} - {e}")
                continue
    
    error_msg = "모든 드라이버 클래스와 JAR 파일 시도 실패"
    print(f"❌ {error_msg}")
    return None, False, error_msg

def test_altibase_connection(conf, test_query):
    """Altibase 연결 테스트 (별도 함수)"""
    import jaydebeapi
    
    # 시도할 드라이버 클래스명들 (올바른 순서로)
    driver_classes = [
        "Altibase.jdbc.driver.AltibaseDriver",
        "com.altibase.jdbc.driver.AltibaseDriver"
    ]
    
    for driver in driver_classes:
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                # 직접 jaydebeapi로 연결 (절대 경로 사용)
                url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
                jar = "/app/db_connection_test/Altibase.jar"  # 절대 경로로 변경
                
                conn = jaydebeapi.connect(driver, url, [conf['user'], conf['password']], jar)
                conn.autocommit = False
                
                # Java 레벨에서 직접 접근
                java_conn = conn.jconn
                java_stmt = java_conn.createStatement()
                java_stmt.setQueryTimeout(30)
                java_result_set = java_stmt.executeQuery(test_query)
                
                # 결과 가져오기
                rows = []
                while java_result_set.next():
                    meta_data = java_result_set.getMetaData()
                    column_count = meta_data.getColumnCount()
                    
                    row = []
                    for i in range(1, column_count + 1):
                        value = java_result_set.getObject(i)
                        row.append(value)
                    
                    rows.append(tuple(row))
                
                # 자원 반납
                java_result_set.close()
                java_stmt.close()
                conn.close()
                
                return rows, True, None
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            if driver == driver_classes[-1]:  # 마지막 시도였다면
                return None, False, f"모든 드라이버 클래스 시도 실패. 마지막 오류: {str(e)}"
            continue  # 다음 드라이버 클래스 시도
    
    return None, False, "드라이버 클래스를 찾을 수 없습니다."

def wait_for_postgres(max_retries=30, retry_interval=2):
    """PostgreSQL이 준비될 때까지 대기"""
    print("🗄️ PostgreSQL 연결 대기 중...")
    
    for attempt in range(max_retries):
        try:
            # PostgreSQL 연결 테스트
            conn = psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', 'postgres'),
                port=os.environ.get('POSTGRES_PORT', 5432),
                database=os.environ.get('POSTGRES_DB', 'fs_master_web'),
                user=os.environ.get('POSTGRES_USER', 'postgres'),
                password=os.environ.get('POSTGRES_PASSWORD')
            )
            conn.close()
            print("✅ PostgreSQL 연결 성공!")
            return True
        except OperationalError as e:
            print(f"⏳ PostgreSQL 연결 시도 {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ PostgreSQL 연결 실패")
                return False
    
    return False

def execute_query_with_columns(server_name, query):
    """컬럼명을 포함한 쿼리 실행"""
    import jaydebeapi
    import psycopg2
    import hashlib
    
    # 작업 디렉토리를 db_connection_test로 변경
    original_cwd = os.getcwd()
    os.chdir('/app/db_connection_test')
    
    try:
        conf = get_server_config(server_name)
        db_type = conf['type']
        
        if db_type == 'postgresql':
            # PostgreSQL 연결
            conn = psycopg2.connect(
                host=conf['host'],
                port=conf['port'],
                database=conf['database'],
                user=conf['user'],
                password=conf['password']
            )
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # 컬럼명 가져오기
            columns = [desc[0] for desc in cursor.description]
            
            # 데이터 가져오기
            rows = cursor.fetchall()
            
            # 각 행에 해시 ID 추가
            result_rows = []
            for i, row in enumerate(rows):
                # 행 데이터를 문자열로 변환하여 해시 생성
                row_str = str(row)
                row_hash = hashlib.md5(row_str.encode()).hexdigest()[:16]  # 16자리 해시
                
                # 해시 ID를 첫 번째 컬럼으로 추가
                new_row = (row_hash,) + row
                result_rows.append(new_row)
            
            # 컬럼명에 ID 컬럼 추가
            result_columns = ['data_hash'] + columns
            
            cursor.close()
            conn.close()
            
            return result_columns, result_rows, True, None
            
        elif db_type == 'altibase':
            # Altibase 연결
            url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
            jar = "/app/db_connection_test/Altibase.jar"
            
            conn = jaydebeapi.connect(
                "com.altibase.jdbc.driver.AltibaseDriver",
                url,
                [conf['user'], conf['password']],
                jar
            )
            
            java_conn = conn.jconn
            java_stmt = java_conn.createStatement()
            java_stmt.setQueryTimeout(30)
            java_result_set = java_stmt.executeQuery(query)
            
            # 컬럼명 가져오기
            meta_data = java_result_set.getMetaData()
            column_count = meta_data.getColumnCount()
            columns = []
            for i in range(1, column_count + 1):
                columns.append(meta_data.getColumnName(i))
            
            # 데이터 가져오기
            rows = []
            while java_result_set.next():
                row = []
                for i in range(1, column_count + 1):
                    value = java_result_set.getObject(i)
                    row.append(value)
                rows.append(tuple(row))
            
            # 각 행에 해시 ID 추가
            result_rows = []
            for i, row in enumerate(rows):
                row_str = str(row)
                row_hash = hashlib.md5(row_str.encode()).hexdigest()[:16]
                new_row = (row_hash,) + row
                result_rows.append(new_row)
            
            # 컬럼명에 ID 컬럼 추가
            result_columns = ['data_hash'] + columns
            
            java_result_set.close()
            java_stmt.close()
            conn.close()
            
            return result_columns, result_rows, True, None
            
        elif db_type == 'informix':
            # Informix 연결
            url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
            jar = "/app/db_connection_test/ifxjdbc.jar"
            
            conn = jaydebeapi.connect(
                "com.informix.jdbc.IfxDriver",
                url,
                [conf['user'], conf['password']],
                jar
            )
            
            java_conn = conn.jconn
            java_stmt = java_conn.createStatement()
            java_stmt.setQueryTimeout(30)
            java_result_set = java_stmt.executeQuery(query)
            
            # 컬럼명 가져오기
            meta_data = java_result_set.getMetaData()
            column_count = meta_data.getColumnCount()
            columns = []
            for i in range(1, column_count + 1):
                columns.append(meta_data.getColumnName(i))
            
            # 데이터 가져오기
            rows = []
            while java_result_set.next():
                row = []
                for i in range(1, column_count + 1):
                    value = java_result_set.getObject(i)
                    row.append(value)
                rows.append(tuple(row))
            
            # 각 행에 해시 ID 추가
            result_rows = []
            for i, row in enumerate(rows):
                row_str = str(row)
                row_hash = hashlib.md5(row_str.encode()).hexdigest()[:16]
                new_row = (row_hash,) + row
                result_rows.append(new_row)
            
            # 컬럼명에 ID 컬럼 추가
            result_columns = ['data_hash'] + columns
            
            java_result_set.close()
            java_stmt.close()
            conn.close()
            
            return result_columns, result_rows, True, None
            
        else:
            return None, None, False, f"지원하지 않는 데이터베이스 타입: {db_type}"
            
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return None, None, False, error_msg
    finally:
        # 작업 디렉토리 복원
        os.chdir(original_cwd)

def execute_incremental_query(server_name, base_query, sync_key_column, last_sync_value, sync_strategy):
    """증분 동기화를 위한 쿼리 실행"""
    import jaydebeapi
    import psycopg2
    import hashlib
    
    # 작업 디렉토리를 db_connection_test로 변경
    original_cwd = os.getcwd()
    os.chdir('/app/db_connection_test')
    
    try:
        conf = get_server_config(server_name)
        db_type = conf['type']
        
        # 증분 동기화 조건 추가
        if sync_strategy == 'timestamp':
            # 타임스탬프 기반 증분 동기화
            if 'WHERE' in base_query.upper():
                incremental_query = f"{base_query} AND {sync_key_column} > '{last_sync_value}'"
            else:
                incremental_query = f"{base_query} WHERE {sync_key_column} > '{last_sync_value}'"
        elif sync_strategy == 'sequence':
            # 시퀀스 기반 증분 동기화
            if 'WHERE' in base_query.upper():
                incremental_query = f"{base_query} AND {sync_key_column} > {last_sync_value}"
            else:
                incremental_query = f"{base_query} WHERE {sync_key_column} > {last_sync_value}"
        elif sync_strategy == 'hash':
            # 해시 기반 증분 동기화 (전체 테이블 스캔 후 해시 비교)
            # 해시 전략에서는 전체 데이터를 가져온 후 타겟과 비교하여 중복 제거
            incremental_query = base_query
        else:
            incremental_query = base_query
        
        print(f"증분 동기화 쿼리: {incremental_query}")
        
        # 기존 execute_query_with_columns 함수 사용
        return execute_query_with_columns(server_name, incremental_query)
        
    except Exception as e:
        import traceback
        error_msg = f"증분 동기화 쿼리 실행 중 오류: {str(e)}\n{traceback.format_exc()}"
        return None, None, False, error_msg
    finally:
        # 작업 디렉토리 복원
        os.chdir(original_cwd)

def get_target_data_hashes(target_conf, table_name):
    """타겟 테이블에서 기존 데이터의 해시값들을 가져오기"""
    try:
        target_db_type = target_conf['type']
        
        if target_db_type == 'postgresql':
            # PostgreSQL에서 해시값 가져오기
            import psycopg2
            conn = psycopg2.connect(
                host=target_conf['host'],
                port=target_conf['port'],
                database=target_conf['database'],
                user=target_conf['user'],
                password=target_conf['password']
            )
            
            cursor = conn.cursor()
            
            # 테이블 존재 여부 확인
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                cursor.close()
                conn.close()
                return set()  # 테이블이 없으면 빈 집합 반환
            
            # data_hash 컬럼에서 해시값들 가져오기
            cursor.execute(f"SELECT data_hash FROM {table_name}")
            existing_hashes = {row[0] for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            return existing_hashes
            
        elif target_db_type == 'altibase':
            # Altibase에서 해시값 가져오기
            import jaydebeapi
            
            url = f"jdbc:Altibase://{target_conf['host']}:{target_conf['port']}/{target_conf['database']}"
            jar = "/app/db_connection_test/Altibase.jar"
            
            conn = jaydebeapi.connect(
                "com.altibase.jdbc.driver.AltibaseDriver",
                url,
                [target_conf['user'], target_conf['password']],
                jar
            )
            
            cursor = conn.jconn.createStatement()
            
            # 테이블 존재 여부 확인
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                table_exists = True
            except:
                table_exists = False
            
            if not table_exists:
                conn.close()
                return set()
            
            # data_hash 컬럼에서 해시값들 가져오기
            result_set = cursor.executeQuery(f"SELECT data_hash FROM {table_name}")
            
            existing_hashes = set()
            while result_set.next():
                existing_hashes.add(result_set.getString(1))
            
            result_set.close()
            conn.close()
            return existing_hashes
            
        elif target_db_type == 'informix':
            # Informix에서 해시값 가져오기
            import jaydebeapi
            
            url = f"jdbc:informix-sqli://{target_conf['host']}:{target_conf['port']}/{target_conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
            jar = "/app/db_connection_test/ifxjdbc.jar"
            
            conn = jaydebeapi.connect(
                "com.informix.jdbc.IfxDriver",
                url,
                [target_conf['user'], target_conf['password']],
                jar
            )
            
            cursor = conn.jconn.createStatement()
            
            # 테이블 존재 여부 확인
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                table_exists = True
            except:
                table_exists = False
            
            if not table_exists:
                conn.close()
                return set()
            
            # data_hash 컬럼에서 해시값들 가져오기
            result_set = cursor.executeQuery(f"SELECT data_hash FROM {table_name}")
            
            existing_hashes = set()
            while result_set.next():
                existing_hashes.add(result_set.getString(1))
            
            result_set.close()
            conn.close()
            return existing_hashes
            
        else:
            return set()
            
    except Exception as e:
        print(f"타겟 데이터 해시 가져오기 실패: {e}")
        return set()

def filter_new_data_by_hash(source_data, target_hashes):
    """해시 기반으로 새로운 데이터만 필터링"""
    if not source_data:
        return []
    
    new_data = []
    for row in source_data:
        if len(row) > 0:
            row_hash = row[0]  # 첫 번째 컬럼이 data_hash
            if row_hash not in target_hashes:
                new_data.append(row)
    
    print(f"해시 기반 필터링: 전체 {len(source_data)}행 중 새로운 데이터 {len(new_data)}행")
    return new_data

def detect_changes(source_data, target_data, sync_key_column):
    """변경사항 감지 (추가, 수정, 삭제)"""
    changes = {
        'added': [],
        'updated': [],
        'deleted': []
    }
    
    # 해시 기반 변경 감지
    source_dict = {}
    target_dict = {}
    
    # 소스 데이터를 해시로 변환
    for row in source_data:
        if len(row) > 0:
            row_hash = row[0]  # 첫 번째 컬럼이 해시 ID
            source_dict[row_hash] = row
    
    # 타겟 데이터를 해시로 변환
    for row in target_data:
        if len(row) > 0:
            row_hash = row[0]  # 첫 번째 컬럼이 해시 ID
            target_dict[row_hash] = row
    
    # 추가된 항목
    for row_hash in source_dict:
        if row_hash not in target_dict:
            changes['added'].append(source_dict[row_hash])
    
    # 삭제된 항목
    for row_hash in target_dict:
        if row_hash not in source_dict:
            changes['deleted'].append(target_dict[row_hash])
    
    # 수정된 항목 (해시가 같지만 내용이 다른 경우)
    for row_hash in source_dict:
        if row_hash in target_dict:
            if source_dict[row_hash] != target_dict[row_hash]:
                changes['updated'].append({
                    'old': target_dict[row_hash],
                    'new': source_dict[row_hash]
                })
    
    return changes

# 데이터베이스 모델
class ServerConfig(db.Model):
    """서버 설정 모델"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    database = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: get_kst_now())
    updated_at = db.Column(db.DateTime, default=lambda: get_kst_now(), onupdate=lambda: get_kst_now())

class BatchJob(db.Model):
    """배치 작업 모델"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    source_server = db.Column(db.String(100), nullable=False)
    query = db.Column(db.Text, nullable=False)
    target_server = db.Column(db.String(100), nullable=False)
    target_table = db.Column(db.String(100), nullable=False)
    chunk_size = db.Column(db.Integer, default=10000)
    num_workers = db.Column(db.Integer, default=4)
    is_active = db.Column(db.Boolean, default=True)
    
    # 증분 동기화 관련 필드
    incremental_sync = db.Column(db.Boolean, default=False)  # 증분 동기화 사용 여부
    sync_key_column = db.Column(db.String(100))  # 동기화 키 컬럼 (예: updated_at, id)
    last_sync_value = db.Column(db.String(200))  # 마지막 동기화 값
    sync_strategy = db.Column(db.String(50), default='timestamp')  # timestamp, sequence, hash
    
    created_at = db.Column(db.DateTime, default=lambda: get_kst_now())
    updated_at = db.Column(db.DateTime, default=lambda: get_kst_now(), onupdate=lambda: get_kst_now())

class BatchSchedule(db.Model):
    """배치 스케줄 모델"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('batch_job.id'), nullable=False)
    cron_expression = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: get_kst_now())
    
    job = db.relationship('BatchJob', backref=db.backref('schedules', lazy=True))

class BatchLog(db.Model):
    """배치 실행 로그 모델"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('batch_job.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('batch_schedule.id'))
    status = db.Column(db.String(20), nullable=False)  # success, failed, running
    total_rows = db.Column(db.Integer)
    total_size_mb = db.Column(db.Float)
    duration_seconds = db.Column(db.Float)
    rows_per_second = db.Column(db.Float)
    mb_per_second = db.Column(db.Float)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=lambda: get_kst_now())
    completed_at = db.Column(db.DateTime)
    
    job = db.relationship('BatchJob', backref=db.backref('logs', lazy=True))
    schedule = db.relationship('BatchSchedule', backref=db.backref('logs', lazy=True))

class QueryHistory(db.Model):
    """쿼리 실행 히스토리 모델"""
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(100), nullable=False)
    query = db.Column(db.Text, nullable=False)
    result_count = db.Column(db.Integer)
    execution_time = db.Column(db.Float)
    status = db.Column(db.String(20), nullable=False)  # success, failed
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=lambda: get_kst_now())

# 설정 파일 관리
class ConfigManager:
    """설정 파일 관리 클래스"""
    
    def __init__(self, config_file='/app/db_connection_test/db_servers.ini'):
        self.config_file = config_file
    
    def load_config(self):
        """설정 파일 로드"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        return config
    
    def save_config(self, config):
        """설정 파일 저장"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
    
    def sync_from_database(self):
        """데이터베이스에서 설정 파일로 동기화"""
        config = configparser.ConfigParser()
        
        servers = db.session.query(ServerConfig).all()
        for server in servers:
            config[server.name] = {
                'type': server.type,
                'host': server.host,
                'port': str(server.port),
                'database': server.database,
                'user': server.user,
                'password': server.password
            }
        
        self.save_config(config)
    
    def sync_to_database(self):
        """설정 파일에서 데이터베이스로 동기화"""
        config = self.load_config()
        
        for section_name in config.sections():
            section = config[section_name]
            
            # 기존 서버 설정 확인
            existing = db.session.query(ServerConfig).filter_by(name=section_name).first()
            
            if existing:
                # 업데이트
                existing.type = section['type']
                existing.host = section['host']
                existing.port = int(section['port'])
                existing.database = section['database']
                existing.user = section['user']
                existing.password = section['password']
            else:
                # 새로 생성
                server = ServerConfig(
                    name=section_name,
                    type=section['type'],
                    host=section['host'],
                    port=int(section['port']),
                    database=section['database'],
                    user=section['user'],
                    password=section['password']
                )
                db.session.add(server)
        
        db.session.commit()

# 배치 작업 실행기
class BatchExecutor:
    """배치 작업 실행 클래스"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def execute_job(self, job_id):
        """배치 작업 실행"""
        job = db.session.get(BatchJob, job_id)
        if not job:
            return False
        
        # 로그 생성
        log = BatchLog(
            job_id=job.id,
            status='running',
            started_at=get_kst_now()
        )
        db.session.add(log)
        db.session.commit()
        
        try:
            # 설정 파일 동기화
            self.config_manager.sync_from_database()
            
            # 쿼리 실행 (데이터베이스 타입에 따라 적절한 함수 사용)
            start_time = time.time()
            
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                # 서버 설정 가져오기
                conf = get_server_config(job.source_server)
                db_type = conf['type']
                
                print(f"=== 배치 작업 실행 시작 ===")
                print(f"작업 ID: {job.id}")
                print(f"작업명: {job.name}")
                print(f"소스 서버: {job.source_server} ({db_type})")
                print(f"타겟 서버: {job.target_server}")
                print(f"쿼리: {job.query}")
                print(f"증분 동기화: {job.incremental_sync}")
                if job.incremental_sync:
                    print(f"동기화 전략: {job.sync_strategy}")
                    print(f"동기화 키 컬럼: {job.sync_key_column}")
                    print(f"마지막 동기화 값: {job.last_sync_value}")
                
                # 증분 동기화가 활성화된 경우 증분 쿼리 실행
                if job.incremental_sync and job.sync_key_column and job.sync_strategy:
                    print("증분 동기화 모드로 실행 중...")
                    columns, source_result, success, error = execute_incremental_query(
                        job.source_server, 
                        job.query, 
                        job.sync_key_column, 
                        job.last_sync_value, 
                        job.sync_strategy
                    )
                else:
                    # 일반 쿼리 실행 (전체 동기화)
                    print("전체 동기화 모드로 실행 중...")
                    columns, source_result, success, error = execute_query_with_columns(job.source_server, job.query)
                
                if not success:
                    raise Exception(f"소스 쿼리 실행 실패: {error}")
                
                print(f"컬럼명: {columns}")
                print(f"데이터 행 수: {len(source_result)}")
                print(f"첫 번째 행 샘플: {source_result[0] if source_result else 'None'}")
                
                # 타겟 데이터베이스에 데이터 저장
                if source_result and len(source_result) > 0:
                    # 타겟 서버 설정 가져오기
                    target_conf = get_server_config(job.target_server)
                    target_db_type = target_conf['type']
                    
                    print(f"타겟 데이터베이스 타입: {target_db_type}")
                    
                    # 해시 기반 증분 동기화인 경우 중복 데이터 필터링
                    if job.incremental_sync and job.sync_strategy == 'hash':
                        print("해시 기반 증분 동기화: 타겟 데이터와 비교하여 중복 제거 중...")
                        target_hashes = get_target_data_hashes(target_conf, job.target_table)
                        print(f"타겟 테이블 기존 해시 수: {len(target_hashes)}")
                        
                        # 중복되지 않는 새로운 데이터만 필터링
                        filtered_result = filter_new_data_by_hash(source_result, target_hashes)
                        
                        if filtered_result:
                            print(f"중복 제거 후 새로운 데이터: {len(filtered_result)}행")
                            source_result = filtered_result
                        else:
                            print("새로운 데이터가 없습니다. 동기화를 건너뜁니다.")
                            # 로그 업데이트
                            log.status = 'success'
                            log.total_rows = 0
                            log.total_size_mb = 0
                            log.duration_seconds = time.time() - start_time
                            log.rows_per_second = 0
                            log.mb_per_second = 0
                            log.completed_at = get_kst_now()
                            db.session.commit()
                            print("배치 작업 성공적으로 완료 (새로운 데이터 없음)")
                            return True
                    
                    # 동기화 전략에 따른 데이터 저장 방식 결정
                    sync_mode = "incremental" if job.incremental_sync else "full"
                    
                    # 타겟 테이블에 데이터 삽입 (컬럼명 포함)
                    if target_db_type == 'postgresql':
                        # PostgreSQL에 저장
                        target_success, target_error, target_result = self._save_to_postgresql_with_columns(
                            target_conf, job.target_table, source_result, columns, sync_mode
                        )
                    elif target_db_type == 'altibase':
                        # Altibase에 저장
                        target_success, target_error, target_result = self._save_to_altibase_with_columns(
                            target_conf, job.target_table, source_result, columns, sync_mode
                        )
                    elif target_db_type == 'informix':
                        # Informix에 저장
                        target_success, target_error, target_result = self._save_to_informix_with_columns(
                            target_conf, job.target_table, source_result, columns, sync_mode
                        )
                    else:
                        raise Exception(f"지원하지 않는 타겟 데이터베이스 타입: {target_db_type}")
                    
                    if not target_success:
                        raise Exception(f"타겟 데이터베이스 저장 실패: {target_error}")
                    else:
                        print(f"타겟 데이터베이스 저장 성공: {target_db_type}")
                        
                        # 증분 동기화가 활성화된 경우 마지막 동기화 값 업데이트
                        if job.incremental_sync and source_result:
                            # 마지막 행의 동기화 키 값을 업데이트
                            last_row = source_result[-1]
                            if job.sync_strategy == 'hash':
                                # 해시 전략인 경우 data_hash 사용
                                job.last_sync_value = last_row[0]  # 첫 번째 컬럼이 data_hash
                                print(f"마지막 동기화 값 업데이트 (해시): {job.last_sync_value}")
                            elif job.sync_key_column in last_row:
                                job.last_sync_value = str(last_row[job.sync_key_column])
                                print(f"마지막 동기화 값 업데이트: {job.last_sync_value}")
                else:
                    print("저장할 데이터가 없습니다.")
                    # 데이터가 없는 경우에도 전체 동기화 모드에서는 기존 데이터 삭제
                    if not job.incremental_sync:
                        print("전체 동기화 모드: 기존 데이터 삭제 수행")
                        target_conf = get_server_config(job.target_server)
                        target_db_type = target_conf['type']
                        
                        if target_db_type == 'postgresql':
                            self._clear_postgresql_table(target_conf, job.target_table)
                        elif target_db_type == 'altibase':
                            self._clear_altibase_table(target_conf, job.target_table)
                        elif target_db_type == 'informix':
                            self._clear_informix_table(target_conf, job.target_table)
                
                end_time = time.time()
                print(f"배치 작업 완료: {end_time - start_time:.2f}초")
                
                # 로그 업데이트
                log.status = 'success'
                log.total_rows = len(source_result) if source_result else 0
                log.total_size_mb = len(source_result) * 0.001 if source_result else 0  # 대략적인 크기
                log.duration_seconds = end_time - start_time
                log.rows_per_second = len(source_result) / (end_time - start_time) if source_result and (end_time - start_time) > 0 else 0
                log.mb_per_second = log.total_size_mb / (end_time - start_time) if (end_time - start_time) > 0 else 0
                log.completed_at = get_kst_now()
                
                print("로그 업데이트 중...")
                db.session.commit()
                print("배치 작업 성공적으로 완료")
                return True
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
            
        except Exception as e:
            # 에러 로그
            log.status = 'failed'
            log.error_message = str(e)
            log.completed_at = get_kst_now()
            db.session.commit()
            return False

    def _save_to_postgresql(self, conf, table_name, data):
        """PostgreSQL에 데이터 저장"""
        import psycopg2
        from psycopg2 import OperationalError
        
        try:
            print(f"PostgreSQL 저장 시작: {conf['host']}:{conf['port']}/{conf['database']}")
            print(f"테이블명: {table_name}, 데이터 행 수: {len(data)}")
            
            conn = psycopg2.connect(
                host=conf['host'],
                port=conf['port'],
                database=conf['database'],
                user=conf['user'],
                password=conf['password']
            )
            conn.autocommit = False  # 트랜잭션 수동 관리
            
            cursor = conn.cursor()
            
            # 테이블 존재 여부 확인 및 생성
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                );
            """)
            table_exists = cursor.fetchone()[0]
            print(f"테이블 존재 여부: {table_exists}")
            
            if not table_exists:
                # 원본 데이터의 구조를 기반으로 테이블 생성
                if data and len(data) > 0:
                    # 첫 번째 행의 구조를 분석
                    first_row = data[0]
                    print(f"첫 번째 행 타입: {type(first_row)}, 길이: {len(first_row) if isinstance(first_row, (list, tuple)) else 'N/A'}")
                    
                    if isinstance(first_row, (list, tuple)):
                        # 튜플/리스트 형태인 경우
                        columns = []
                        for i, value in enumerate(first_row):
                            if isinstance(value, int):
                                columns.append(f"col_{i} INTEGER")
                            elif isinstance(value, float):
                                columns.append(f"col_{i} NUMERIC")
                            elif isinstance(value, bool):
                                columns.append(f"col_{i} BOOLEAN")
                            else:
                                columns.append(f"col_{i} TEXT")
                        
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id SERIAL PRIMARY KEY,
                                {', '.join(columns)}
                            );
                        """
                        print(f"생성할 테이블 SQL: {create_sql}")
                    else:
                        # 딕셔너리 형태인 경우
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id SERIAL PRIMARY KEY,
                                data JSONB NOT NULL
                            );
                        """
                else:
                    # 기본 구조
                    create_sql = f"""
                        CREATE TABLE {table_name} (
                            id SERIAL PRIMARY KEY,
                            data JSONB NOT NULL
                        );
                    """
                
                cursor.execute(create_sql)
                conn.commit()
                print(f"테이블 {table_name}이 생성되었습니다.")
            
            # 배치 처리를 위한 준비
            batch_size = 1000
            total_rows = len(data)
            print(f"배치 처리 시작: 총 {total_rows}행, 배치 크기: {batch_size}")
            
            # 데이터 삽입 (배치 처리)
            for i in range(0, total_rows, batch_size):
                batch_data = data[i:i + batch_size]
                print(f"배치 {i//batch_size + 1} 처리 중: {i+1}~{min(i + batch_size, total_rows)}행")
                
                if isinstance(batch_data[0], (list, tuple)):
                    # 튜플/리스트 형태인 경우
                    values = []
                    for row in batch_data:
                        placeholders = ', '.join(['%s'] * len(row))
                        values.append(cursor.mogrify(f"({placeholders})", row).decode('utf-8'))
                    
                    if values:
                        # 컬럼명을 동적으로 생성
                        column_names = [f"col_{i}" for i in range(len(batch_data[0]))]
                        column_list = ', '.join(column_names)
                        
                        insert_sql = f"""
                            INSERT INTO {table_name} ({column_list}) 
                            VALUES {','.join(values)};
                        """
                        print(f"INSERT SQL 실행: {len(values)}행")
                        cursor.execute(insert_sql)
                else:
                    # 딕셔너리 형태인 경우
                    values = []
                    for row in batch_data:
                        values.append(cursor.mogrify("(%s)", (json.dumps(row, ensure_ascii=False),)).decode('utf-8'))
                    
                    if values:
                        cursor.execute(f"""
                            INSERT INTO {table_name} (data) VALUES {','.join(values)};
                        """)
                
                # 배치마다 커밋
                conn.commit()
                print(f"배치 처리 완료: {min(i + batch_size, total_rows)}/{total_rows}")
            
            print("PostgreSQL 저장 완료")
            return True, None, None
            
        except OperationalError as e:
            error_msg = f"PostgreSQL 데이터베이스 저장 중 오류: {e}"
            print(error_msg)
            return False, error_msg, None
        except Exception as e:
            import traceback
            error_msg = f"PostgreSQL 데이터베이스 저장 중 예외 발생: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False, error_msg, None
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def _save_to_altibase(self, conf, table_name, data):
        """Altibase에 데이터 저장"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
                jar = "/app/db_connection_test/Altibase.jar"
                
                conn = jaydebeapi.connect(
                    "com.altibase.jdbc.driver.AltibaseDriver",
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = False  # 트랜잭션 수동 관리
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인 및 생성
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                    """)
                    table_exists = True
                except:
                    table_exists = False
                
                if not table_exists:
                    # 원본 데이터의 구조를 기반으로 테이블 생성
                    if data and len(data) > 0:
                        first_row = data[0]
                        if isinstance(first_row, (list, tuple)) and len(first_row) <= 10:  # Altibase는 컬럼 수 제한이 있을 수 있음
                            # 튜플/리스트 형태인 경우 (컬럼 수가 적을 때만)
                            columns = []
                            for i, value in enumerate(first_row):
                                if isinstance(value, int):
                                    columns.append(f"col_{i} INTEGER")
                                elif isinstance(value, float):
                                    columns.append(f"col_{i} NUMERIC")
                                elif isinstance(value, bool):
                                    columns.append(f"col_{i} SMALLINT")  # Altibase에서 BOOLEAN 대신 SMALLINT 사용
                                else:
                                    columns.append(f"col_{i} VARCHAR(1000)")
                            
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id INTEGER PRIMARY KEY,
                                    {', '.join(columns)}
                                );
                            """
                        else:
                            # 컬럼이 많거나 복잡한 경우 JSON 형태로 저장
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id INTEGER PRIMARY KEY,
                                    data VARCHAR(4000)
                                );
                            """
                    else:
                        # 기본 구조
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id INTEGER PRIMARY KEY,
                                data VARCHAR(4000)
                            );
                        """
                    
                    cursor.execute(create_sql)
                    conn.jconn.commit()
                    print(f"테이블 {table_name}이 생성되었습니다.")
                
                # 배치 처리를 위한 준비
                batch_size = 1000
                total_rows = len(data)
                
                # 데이터 삽입 (배치 처리)
                for i in range(0, total_rows, batch_size):
                    batch_data = data[i:i + batch_size]
                    
                    for j, row in enumerate(batch_data):
                        row_id = i + j + 1  # 고유한 ID 생성
                        
                        # 테이블 구조에 따라 적절한 INSERT 사용
                        if isinstance(row, (list, tuple)) and len(row) <= 10:
                            # 컬럼별 저장
                            placeholders = ', '.join(['?'] * len(row))
                            column_names = [f"col_{k}" for k in range(len(row))]
                            column_list = ', '.join(column_names)
                            
                            cursor.execute(f"""
                                INSERT INTO {table_name} (id, {column_list}) VALUES (?, {placeholders});
                            """, [row_id] + list(row))
                        else:
                            # JSON 형태로 저장
                            row_data = json.dumps(row, ensure_ascii=False)[:3990]  # Altibase VARCHAR 제한
                            
                            cursor.execute(f"""
                                INSERT INTO {table_name} (id, data) VALUES (?, ?);
                            """, (row_id, row_data))
                    
                    # 배치마다 커밋
                    conn.jconn.commit()
                    print(f"배치 처리 완료: {min(i + batch_size, total_rows)}/{total_rows}")
                
                return True, None, None
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            return False, f"Altibase 데이터베이스 저장 중 예외 발생: {e}", None

    def _save_to_informix(self, conf, table_name, data):
        """Informix에 데이터 저장"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
                jar = "/app/db_connection_test/ifxjdbc.jar"
                
                conn = jaydebeapi.connect(
                    "com.informix.jdbc.IfxDriver",
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = True # 자동 커밋 활성화
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인 및 생성
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM DUAL
                        WHERE EXISTS (
                            SELECT FROM sysmaster:sys_tables WHERE table_name = '{table_name}'
                        )
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    cursor.execute(f"""
                        CREATE TABLE {table_name} (
                            id INTEGER PRIMARY KEY,
                            data JSONB NOT NULL
                        );
                    """)
                    conn.jconn.commit()
                    print(f"테이블 {table_name}이 생성되었습니다.")
                
                # 데이터 삽입
                for row in data:
                    cursor.execute(f"""
                        INSERT INTO {table_name} (id, data) VALUES (?, ?);
                    """, (len(data) + 1, json.dumps(row))) # Informix는 자동 증가 키 사용
                
                conn.jconn.commit()
                return True, None, None
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            return False, f"Informix 데이터베이스 저장 중 예외 발생: {e}", None

    def _save_to_postgresql_with_columns(self, conf, table_name, data, columns, sync_mode="full"):
        """PostgreSQL에 데이터 저장 (컬럼명 포함) - 동기화 전략 적용"""
        import psycopg2
        from psycopg2 import OperationalError
        
        try:
            print(f"PostgreSQL 저장 시작: {conf['host']}:{conf['port']}/{conf['database']}")
            print(f"테이블명: {table_name}, 데이터 행 수: {len(data)}, 동기화 모드: {sync_mode}")
            
            conn = psycopg2.connect(
                host=conf['host'],
                port=conf['port'],
                database=conf['database'],
                user=conf['user'],
                password=conf['password']
            )
            conn.autocommit = False  # 트랜잭션 수동 관리
            
            cursor = conn.cursor()
            
            # 테이블 존재 여부 확인 및 생성
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                );
            """)
            table_exists = cursor.fetchone()[0]
            print(f"테이블 존재 여부: {table_exists}")
            
            if not table_exists:
                # 원본 데이터의 구조를 기반으로 테이블 생성
                if data and len(data) > 0:
                    # 첫 번째 행의 구조를 분석
                    first_row = data[0]
                    print(f"첫 번째 행 타입: {type(first_row)}, 길이: {len(first_row) if isinstance(first_row, (list, tuple)) else 'N/A'}")
                    
                    if isinstance(first_row, (list, tuple)):
                        # 튜플/리스트 형태인 경우
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id SERIAL PRIMARY KEY,
                                {', '.join([f'{col} TEXT' for col in columns])}
                            );
                        """
                        print(f"생성할 테이블 SQL: {create_sql}")
                    else:
                        # 딕셔너리 형태인 경우
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id SERIAL PRIMARY KEY,
                                data JSONB NOT NULL
                            );
                        """
                else:
                    # 기본 구조
                    create_sql = f"""
                        CREATE TABLE {table_name} (
                            id SERIAL PRIMARY KEY,
                            data JSONB NOT NULL
                        );
                    """
                
                cursor.execute(create_sql)
                conn.commit()
                print(f"테이블 {table_name}이 생성되었습니다.")
            
            # 동기화 모드에 따른 처리
            if sync_mode == "full":
                # 전체 동기화: 기존 데이터 삭제 후 새 데이터 삽입
                print("전체 동기화 전략 적용: 기존 데이터 삭제 후 새 데이터 삽입")
                
                # 기존 데이터 삭제
                cursor.execute(f"DELETE FROM {table_name}")
                deleted_count = cursor.rowcount
                print(f"기존 데이터 삭제 완료: {deleted_count}행")
                
                # 새 데이터 삽입
                if data and len(data) > 0:
                    self._insert_postgresql_data(cursor, table_name, data, columns)
                    print(f"PostgreSQL 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 {len(data)}행")
                else:
                    print(f"PostgreSQL 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 0행")
                    
            elif sync_mode == "incremental":
                # 증분 동기화: 새 데이터만 추가 (삭제된 데이터는 별도 처리 필요)
                print("증분 동기화 전략 적용: 새 데이터만 추가")
                
                if data and len(data) > 0:
                    # 중복 제거를 위한 임시 테이블 사용
                    temp_table = f"{table_name}_temp_{int(time.time())}"
                    
                    # 임시 테이블 생성 및 데이터 삽입
                    cursor.execute(f"CREATE TABLE {temp_table} AS SELECT * FROM {table_name} WHERE 1=0")
                    self._insert_postgresql_data(cursor, temp_table, data, columns)
                    
                    # 기존 테이블과 병합 (중복 제거)
                    if isinstance(data[0], (list, tuple)) and len(columns) > 0:
                        # 컬럼 기반 중복 제거
                        merge_sql = f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            SELECT {', '.join(columns)} FROM {temp_table}
                            ON CONFLICT DO NOTHING;
                        """
                    else:
                        # JSON 기반 중복 제거
                        merge_sql = f"""
                            INSERT INTO {table_name} (data)
                            SELECT data FROM {temp_table}
                            ON CONFLICT DO NOTHING;
                        """
                    
                    cursor.execute(merge_sql)
                    inserted_count = cursor.rowcount
                    
                    # 임시 테이블 삭제
                    cursor.execute(f"DROP TABLE {temp_table}")
                    
                    print(f"PostgreSQL 증분 동기화 완료: 추가 {inserted_count}행")
                else:
                    print("PostgreSQL 증분 동기화 완료: 새로운 데이터 없음")
            
            conn.commit()
            return True, None, None
            
        except OperationalError as e:
            error_msg = f"PostgreSQL 데이터베이스 저장 중 오류: {e}"
            print(error_msg)
            return False, error_msg, None
        except Exception as e:
            import traceback
            error_msg = f"PostgreSQL 데이터베이스 저장 중 예외 발생: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False, error_msg, None
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def _insert_postgresql_data(self, cursor, table_name, data, columns):
        """PostgreSQL에 데이터 삽입 (헬퍼 함수)"""
        # 배치 처리를 위한 준비
        batch_size = 1000
        total_rows = len(data)
        print(f"배치 처리 시작: 총 {total_rows}행, 배치 크기: {batch_size}")
        
        # 데이터 삽입 (배치 처리)
        for i in range(0, total_rows, batch_size):
            batch_data = data[i:i + batch_size]
            print(f"배치 {i//batch_size + 1} 처리 중: {i+1}~{min(i + batch_size, total_rows)}행")
            
            if isinstance(batch_data[0], (list, tuple)):
                # 튜플/리스트 형태인 경우
                values = []
                for row in batch_data:
                    placeholders = ', '.join(['%s'] * len(row))
                    values.append(cursor.mogrify(f"({placeholders})", row).decode('utf-8'))
                
                if values:
                    # 컬럼명을 동적으로 생성
                    column_list = ', '.join(columns)
                    
                    insert_sql = f"""
                        INSERT INTO {table_name} ({column_list}) 
                        VALUES {','.join(values)};
                    """
                    print(f"INSERT SQL 실행: {len(values)}행")
                    cursor.execute(insert_sql)
            else:
                # 딕셔너리 형태인 경우
                values = []
                for row in batch_data:
                    values.append(cursor.mogrify("(%s)", (json.dumps(row, ensure_ascii=False),)).decode('utf-8'))
                
                if values:
                    cursor.execute(f"""
                        INSERT INTO {table_name} (data) VALUES {','.join(values)};
                    """)
            
            print(f"배치 처리 완료: {min(i + batch_size, total_rows)}/{total_rows}")
    
    def _clear_postgresql_table(self, conf, table_name):
        """PostgreSQL 테이블의 모든 데이터 삭제"""
        import psycopg2
        from psycopg2 import OperationalError
        
        try:
            conn = psycopg2.connect(
                host=conf['host'],
                port=conf['port'],
                database=conf['database'],
                user=conf['user'],
                password=conf['password']
            )
            conn.autocommit = False
            
            cursor = conn.cursor()
            
            # 테이블 존재 여부 확인
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                cursor.execute(f"DELETE FROM {table_name}")
                deleted_count = cursor.rowcount
                conn.commit()
                print(f"PostgreSQL 테이블 {table_name} 데이터 삭제 완료: {deleted_count}행")
            else:
                print(f"PostgreSQL 테이블 {table_name}이 존재하지 않습니다.")
            
            return True
            
        except Exception as e:
            print(f"PostgreSQL 테이블 삭제 중 오류: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def _save_to_altibase_with_columns(self, conf, table_name, data, columns, sync_mode="full"):
        """Altibase에 데이터 저장 (컬럼명 포함) - 동기화 전략 적용"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                print(f"Altibase 저장 시작: {conf['host']}:{conf['port']}/{conf['database']}")
                print(f"테이블명: {table_name}, 데이터 행 수: {len(data)}, 동기화 모드: {sync_mode}")
                
                url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
                jar = "/app/db_connection_test/Altibase.jar"
                
                conn = jaydebeapi.connect(
                    "Altibase.jdbc.driver.AltibaseDriver",
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = False  # 트랜잭션 수동 관리
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인 및 생성
                cursor.execute(f"""
                    SELECT COUNT(*) FROM SYSTEM_.SYS_TABLES_ WHERE TABLE_NAME = '{table_name}'
                """)
                table_exists = cursor.fetchone()[0] > 0
                print(f"테이블 존재 여부: {table_exists}")
                
                if not table_exists:
                    # 테이블 생성
                    if data and len(data) > 0:
                        # 첫 번째 행의 구조를 분석
                        first_row = data[0]
                        if isinstance(first_row, (list, tuple)) and len(first_row) <= 10:
                            # 컬럼별 저장 (컬럼 수가 적을 때만)
                            columns = []
                            for i, value in enumerate(first_row):
                                if isinstance(value, int):
                                    columns.append(f"col_{i} INTEGER")
                                elif isinstance(value, float):
                                    columns.append(f"col_{i} NUMERIC")
                                elif isinstance(value, bool):
                                    columns.append(f"col_{i} SMALLINT")  # Altibase에서 BOOLEAN 대신 SMALLINT 사용
                                else:
                                    columns.append(f"col_{i} VARCHAR(1000)")
                            
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id INTEGER PRIMARY KEY,
                                    {', '.join(columns)}
                                );
                            """
                        else:
                            # JSON 형태로 저장
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id INTEGER PRIMARY KEY,
                                    data VARCHAR(4000)
                                );
                            """
                    else:
                        # 기본 구조
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id INTEGER PRIMARY KEY,
                                data VARCHAR(4000)
                            );
                        """
                    
                    cursor.execute(create_sql)
                    conn.jconn.commit()
                    print(f"테이블 {table_name}이 생성되었습니다.")
                
                # 동기화 모드에 따른 처리
                if sync_mode == "full":
                    # 전체 동기화: 기존 데이터 삭제 후 새 데이터 삽입
                    print("전체 동기화 전략 적용: 기존 데이터 삭제 후 새 데이터 삽입")
                    
                    # 기존 데이터 삭제
                    cursor.execute(f"DELETE FROM {table_name}")
                    deleted_count = cursor.rowcount
                    print(f"기존 데이터 삭제 완료: {deleted_count}행")
                    
                    # 새 데이터 삽입
                    if data and len(data) > 0:
                        self._insert_altibase_data(cursor, table_name, data, columns)
                        print(f"Altibase 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 {len(data)}행")
                    else:
                        print(f"Altibase 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 0행")
                        
                elif sync_mode == "incremental":
                    # 증분 동기화: 새 데이터만 추가 (중복 제거)
                    print("증분 동기화 전략 적용: 새 데이터만 추가")
                    
                    if data and len(data) > 0:
                        # 중복 제거를 위한 임시 테이블 사용
                        temp_table = f"{table_name}_temp_{int(time.time())}"
                        
                        # 임시 테이블 생성
                        cursor.execute(f"CREATE TABLE {temp_table} AS SELECT * FROM {table_name} WHERE 1=0")
                        self._insert_altibase_data(cursor, temp_table, data, columns)
                        
                        # 기존 테이블과 병합 (중복 제거)
                        if isinstance(data[0], (list, tuple)) and len(columns) > 0:
                            # 컬럼 기반 중복 제거
                            merge_sql = f"""
                                INSERT INTO {table_name} ({', '.join(columns)})
                                SELECT {', '.join(columns)} FROM {temp_table}
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} t2 
                                    WHERE t2.{columns[0]} = {temp_table}.{columns[0]}
                                );
                            """
                        else:
                            # JSON 기반 중복 제거
                            merge_sql = f"""
                                INSERT INTO {table_name} (data)
                                SELECT data FROM {temp_table}
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} t2 
                                    WHERE t2.data = {temp_table}.data
                                );
                            """
                        
                        cursor.execute(merge_sql)
                        inserted_count = cursor.rowcount
                        
                        # 임시 테이블 삭제
                        cursor.execute(f"DROP TABLE {temp_table}")
                        
                        print(f"Altibase 증분 동기화 완료: 추가 {inserted_count}행")
                    else:
                        print("Altibase 증분 동기화 완료: 새로운 데이터 없음")
                
                conn.jconn.commit()
                return True, None, None
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            import traceback
            error_msg = f"Altibase 데이터베이스 저장 중 예외 발생: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False, error_msg, None
    
    def _insert_altibase_data(self, cursor, table_name, data, columns):
        """Altibase에 데이터 삽입 (헬퍼 함수)"""
        # 배치 처리를 위한 준비
        batch_size = 1000
        total_rows = len(data)
        print(f"배치 처리 시작: 총 {total_rows}행, 배치 크기: {batch_size}")
        
        # 데이터 삽입 (배치 처리)
        for i in range(0, total_rows, batch_size):
            batch_data = data[i:i + batch_size]
            print(f"배치 {i//batch_size + 1} 처리 중: {i+1}~{min(i + batch_size, total_rows)}행")
            
            for row_id, row in enumerate(batch_data, i + 1):
                # 테이블 구조에 따라 적절한 INSERT 사용
                if isinstance(row, (list, tuple)) and len(row) <= 10:
                    # 컬럼별 저장
                    placeholders = ', '.join(['?'] * len(row))
                    column_list = ', '.join(columns)
                    
                    cursor.execute(f"""
                        INSERT INTO {table_name} (id, {column_list}) VALUES (?, {placeholders});
                    """, [row_id] + list(row))
                else:
                    # JSON 형태로 저장
                    row_data = json.dumps(row, ensure_ascii=False)[:3990]  # Altibase VARCHAR 제한
                    
                    cursor.execute(f"""
                        INSERT INTO {table_name} (id, data) VALUES (?, ?);
                    """, (row_id, row_data))
            
            print(f"배치 처리 완료: {min(i + batch_size, total_rows)}/{total_rows}")
    
    def _clear_altibase_table(self, conf, table_name):
        """Altibase 테이블의 모든 데이터 삭제"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
                jar = "/app/db_connection_test/Altibase.jar"
                
                conn = jaydebeapi.connect(
                    "Altibase.jdbc.driver.AltibaseDriver",
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = False
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인
                cursor.execute(f"""
                    SELECT COUNT(*) FROM SYSTEM_.SYS_TABLES_ WHERE TABLE_NAME = '{table_name}'
                """)
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists:
                    cursor.execute(f"DELETE FROM {table_name}")
                    deleted_count = cursor.rowcount
                    conn.jconn.commit()
                    print(f"Altibase 테이블 {table_name} 데이터 삭제 완료: {deleted_count}행")
                else:
                    print(f"Altibase 테이블 {table_name}이 존재하지 않습니다.")
                
                return True
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Altibase 테이블 삭제 중 오류: {e}")
            return False

    def _save_to_informix_with_columns(self, conf, table_name, data, columns, sync_mode="full"):
        """Informix에 데이터 저장 (컬럼명 포함) - 동기화 전략 적용"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                print(f"Informix 저장 시작: {conf['host']}:{conf['port']}/{conf['database']}")
                print(f"테이블명: {table_name}, 데이터 행 수: {len(data)}, 동기화 모드: {sync_mode}")
                
                url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
                jar = "/app/db_connection_test/ifxjdbc.jar"
                
                conn = jaydebeapi.connect(
                    "com.informix.jdbc.IfxDriver",  # 올바른 드라이버 클래스명 사용
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = False  # 트랜잭션 수동 관리
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인 및 생성
                cursor.execute(f"""
                    SELECT COUNT(*) FROM sysmaster:sys_tables WHERE tabname = '{table_name}'
                """)
                table_exists = cursor.fetchone()[0] > 0
                print(f"테이블 존재 여부: {table_exists}")
                
                if not table_exists:
                    # 테이블 생성
                    if data and len(data) > 0:
                        # 첫 번째 행의 구조를 분석
                        first_row = data[0]
                        if isinstance(first_row, (list, tuple)):
                            # 튜플/리스트 형태인 경우
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id SERIAL PRIMARY KEY,
                                    {', '.join([f'{col} VARCHAR(1000)' for col in columns])}
                                );
                            """
                        else:
                            # 딕셔너리 형태인 경우
                            create_sql = f"""
                                CREATE TABLE {table_name} (
                                    id SERIAL PRIMARY KEY,
                                    data TEXT
                                );
                            """
                    else:
                        # 기본 구조
                        create_sql = f"""
                            CREATE TABLE {table_name} (
                                id SERIAL PRIMARY KEY,
                                data TEXT
                            );
                        """
                    
                    cursor.execute(create_sql)
                    conn.jconn.commit()
                    print(f"테이블 {table_name}이 생성되었습니다.")
                
                # 동기화 모드에 따른 처리
                if sync_mode == "full":
                    # 전체 동기화: 기존 데이터 삭제 후 새 데이터 삽입
                    print("전체 동기화 전략 적용: 기존 데이터 삭제 후 새 데이터 삽입")
                    
                    # 기존 데이터 삭제
                    cursor.execute(f"DELETE FROM {table_name}")
                    deleted_count = cursor.rowcount
                    print(f"기존 데이터 삭제 완료: {deleted_count}행")
                    
                    # 새 데이터 삽입
                    if data and len(data) > 0:
                        self._insert_informix_data(cursor, table_name, data, columns)
                        print(f"Informix 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 {len(data)}행")
                    else:
                        print(f"Informix 전체 동기화 완료: 삭제 {deleted_count}행, 삽입 0행")
                        
                elif sync_mode == "incremental":
                    # 증분 동기화: 새 데이터만 추가 (중복 제거)
                    print("증분 동기화 전략 적용: 새 데이터만 추가")
                    
                    if data and len(data) > 0:
                        # 중복 제거를 위한 임시 테이블 사용
                        temp_table = f"{table_name}_temp_{int(time.time())}"
                        
                        # 임시 테이블 생성
                        cursor.execute(f"CREATE TABLE {temp_table} AS SELECT * FROM {table_name} WHERE 1=0")
                        self._insert_informix_data(cursor, temp_table, data, columns)
                        
                        # 기존 테이블과 병합 (중복 제거)
                        if isinstance(data[0], (list, tuple)) and len(columns) > 0:
                            # 컬럼 기반 중복 제거
                            merge_sql = f"""
                                INSERT INTO {table_name} ({', '.join(columns)})
                                SELECT {', '.join(columns)} FROM {temp_table}
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} t2 
                                    WHERE t2.{columns[0]} = {temp_table}.{columns[0]}
                                );
                            """
                        else:
                            # JSON 기반 중복 제거
                            merge_sql = f"""
                                INSERT INTO {table_name} (data)
                                SELECT data FROM {temp_table}
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM {table_name} t2 
                                    WHERE t2.data = {temp_table}.data
                                );
                            """
                        
                        cursor.execute(merge_sql)
                        inserted_count = cursor.rowcount
                        
                        # 임시 테이블 삭제
                        cursor.execute(f"DROP TABLE {temp_table}")
                        
                        print(f"Informix 증분 동기화 완료: 추가 {inserted_count}행")
                    else:
                        print("Informix 증분 동기화 완료: 새로운 데이터 없음")
                    
                conn.jconn.commit()
                return True, None, None
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            import traceback
            error_msg = f"Informix 데이터베이스 저장 중 예외 발생: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False, error_msg, None
    
    def _insert_informix_data(self, cursor, table_name, data, columns):
        """Informix에 데이터 삽입 (헬퍼 함수)"""
        # 배치 처리를 위한 준비
        batch_size = 1000
        total_rows = len(data)
        print(f"배치 처리 시작: 총 {total_rows}행, 배치 크기: {batch_size}")
        
        # 데이터 삽입 (배치 처리)
        for i in range(0, total_rows, batch_size):
            batch_data = data[i:i + batch_size]
            print(f"배치 {i//batch_size + 1} 처리 중: {i+1}~{min(i + batch_size, total_rows)}행")
            
            for row in batch_data:
                if isinstance(row, (list, tuple)):
                    # 튜플/리스트 형태인 경우
                    placeholders = ', '.join(['?'] * len(row))
                    column_list = ', '.join(columns)
                    
                    cursor.execute(f"""
                        INSERT INTO {table_name} ({column_list}) VALUES ({placeholders});
                    """, list(row))
                else:
                    # 딕셔너리 형태인 경우
                    row_data = json.dumps(row, ensure_ascii=False)
                    cursor.execute(f"""
                        INSERT INTO {table_name} (data) VALUES (?);
                    """, (row_data,))
            
            print(f"배치 처리 완료: {min(i + batch_size, total_rows)}/{total_rows}")
    
    def _clear_informix_table(self, conf, table_name):
        """Informix 테이블의 모든 데이터 삭제"""
        import jaydebeapi
        
        try:
            # 작업 디렉토리를 db_connection_test로 변경
            original_cwd = os.getcwd()
            os.chdir('/app/db_connection_test')
            
            try:
                url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
                jar = "/app/db_connection_test/ifxjdbc.jar"
                
                conn = jaydebeapi.connect(
                    "com.informix.jdbc.IfxDriver",
                    url,
                    [conf['user'], conf['password']],
                    jar
                )
                conn.autocommit = False
                
                cursor = conn.jconn.createStatement()
                
                # 테이블 존재 여부 확인
                cursor.execute(f"""
                    SELECT COUNT(*) FROM sysmaster:sys_tables WHERE tabname = '{table_name}'
                """)
                table_exists = cursor.fetchone()[0] > 0
                
                if table_exists:
                    cursor.execute(f"DELETE FROM {table_name}")
                    deleted_count = cursor.rowcount
                    conn.jconn.commit()
                    print(f"Informix 테이블 {table_name} 데이터 삭제 완료: {deleted_count}행")
                else:
                    print(f"Informix 테이블 {table_name}이 존재하지 않습니다.")
                
                return True
                
            finally:
                # 작업 디렉토리 복원
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Informix 테이블 삭제 중 오류: {e}")
            return False

# 라우트
@app.context_processor
def inject_kst_functions():
    """템플릿에서 사용할 KST 관련 함수들을 주입"""
    return {
        'format_kst_time': format_kst_time,
        'format_db_kst_time': format_db_kst_time,
        'format_scheduler_time': format_scheduler_time,
        'get_kst_now': get_kst_now,
        'utc_to_kst': utc_to_kst,
        'parse_cron_expression': parse_cron_expression
    }

@app.route('/')
def index():
    """메인 페이지"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """대시보드"""
    # 통계 정보
    total_jobs = db.session.query(BatchJob).count()
    active_jobs = db.session.query(BatchJob).filter_by(is_active=True).count()
    total_schedules = db.session.query(BatchSchedule).count()
    active_schedules = db.session.query(BatchSchedule).filter_by(is_active=True).count()
    
    # 최근 로그
    recent_logs = db.session.query(BatchLog).order_by(BatchLog.started_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_jobs=total_jobs,
                         active_jobs=active_jobs,
                         total_schedules=total_schedules,
                         active_schedules=active_schedules,
                         recent_logs=recent_logs)

@app.route('/servers')
def servers():
    """서버 관리 페이지"""
    servers = db.session.query(ServerConfig).all()
    return render_template('servers.html', servers=servers)

@app.route('/servers/add', methods=['GET', 'POST'])
def add_server():
    """서버 추가"""
    if request.method == 'POST':
        data = request.form
        
        server = ServerConfig(
            name=data['name'],
            type=data['type'],
            host=data['host'],
            port=int(data['port']),
            database=data['database'],
            user=data['user'],
            password=data['password']
        )
        
        db.session.add(server)
        db.session.commit()
        
        # 설정 파일 동기화
        config_manager = ConfigManager()
        config_manager.sync_from_database()
        
        flash('서버가 추가되었습니다.', 'success')
        return redirect(url_for('servers'))
    
    return render_template('add_server.html')

@app.route('/servers/<int:server_id>/edit', methods=['GET', 'POST'])
def edit_server(server_id):
    """서버 수정"""
    server = db.session.query(ServerConfig).get_or_404(server_id)
    
    if request.method == 'POST':
        data = request.form
        
        server.name = data['name']
        server.type = data['type']
        server.host = data['host']
        server.port = int(data['port'])
        server.database = data['database']
        server.user = data['user']
        server.password = data['password']
        
        db.session.commit()
        
        # 설정 파일 동기화
        config_manager = ConfigManager()
        config_manager.sync_from_database()
        
        flash('서버가 수정되었습니다.', 'success')
        return redirect(url_for('servers'))
    
    return render_template('edit_server.html', server=server)

@app.route('/servers/<int:server_id>/delete', methods=['POST'])
def delete_server(server_id):
    """서버 삭제"""
    server = db.session.query(ServerConfig).get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    
    # 설정 파일 동기화
    config_manager = ConfigManager()
    config_manager.sync_from_database()
    
    flash('서버가 삭제되었습니다.', 'success')
    return redirect(url_for('servers'))

@app.route('/query')
def query():
    """쿼리 실행 페이지"""
    servers = db.session.query(ServerConfig).all()
    return render_template('query.html', servers=servers)

@app.route('/query/execute', methods=['POST'])
def execute_query():
    """쿼리 실행"""
    data = request.json
    
    try:
        # 설정 파일 동기화
        config_manager = ConfigManager()
        config_manager.sync_from_database()
        
        # 작업 디렉토리를 db_connection_test로 변경
        original_cwd = os.getcwd()
        os.chdir('/app/db_connection_test')
        
        try:
            # 쿼리 실행 (원래 db_query.py의 execute_query 사용)
            start_time = time.time()
            result, success, error = db_execute_query(data['server'], data['query'])
            end_time = time.time()
            
            if not success:
                raise Exception(f"쿼리 실행 실패: {error}")
            
            # 히스토리 저장
            history = QueryHistory(
                server_name=data['server'],
                query=data['query'],
                result_count=len(result) if result else 0,
                execution_time=end_time - start_time,
                status='success'
            )
            db.session.add(history)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'result': {
                    'columns': [],  # 원래 execute_query는 컬럼명을 반환하지 않음
                    'rows': result,
                    'row_count': len(result) if result else 0
                }
            })
        finally:
            # 작업 디렉토리 복원
            os.chdir(original_cwd)
        
    except Exception as e:
        # 에러 히스토리 저장
        history = QueryHistory(
            server_name=data['server'],
            query=data['query'],
            status='failed',
            error_message=str(e)
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/jobs')
def jobs():
    """배치 작업 관리 페이지"""
    jobs = db.session.query(BatchJob).all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    """배치 작업 추가"""
    if request.method == 'POST':
        data = request.form
        
        job = BatchJob(
            name=data['name'],
            description=data['description'],
            source_server=data['source_server'],
            query=data['query'],
            target_server=data['target_server'],
            target_table=data['target_table'],
            chunk_size=int(data['chunk_size']),
            num_workers=int(data['num_workers']),
            is_active='is_active' in data,
            # 증분 동기화 관련 필드 추가
            incremental_sync='incremental_sync' in data,
            sync_key_column=data.get('sync_key_column', ''),
            last_sync_value=data.get('last_sync_value', ''),
            sync_strategy=data.get('sync_strategy', 'timestamp')
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('배치 작업이 추가되었습니다.', 'success')
        return redirect(url_for('jobs'))
    
    servers = db.session.query(ServerConfig).all()
    return render_template('add_job.html', servers=servers)

@app.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    """배치 작업 수정"""
    job = db.session.get(BatchJob, job_id)
    if not job:
        abort(404)
    
    if request.method == 'POST':
        data = request.form
        
        job.name = data['name']
        job.description = data['description']
        job.source_server = data['source_server']
        job.query = data['query']
        job.target_server = data['target_server']
        job.target_table = data['target_table']
        job.chunk_size = int(data['chunk_size'])
        job.num_workers = int(data['num_workers'])
        job.is_active = 'is_active' in data
        
        # 증분 동기화 관련 필드 추가
        job.incremental_sync = 'incremental_sync' in data
        job.sync_key_column = data.get('sync_key_column', '')
        job.last_sync_value = data.get('last_sync_value', '')
        job.sync_strategy = data.get('sync_strategy', 'timestamp')
        
        db.session.commit()
        
        flash('배치 작업이 수정되었습니다.', 'success')
        return redirect(url_for('jobs'))
    
    servers = db.session.query(ServerConfig).all()
    return render_template('edit_job.html', job=job, servers=servers)

@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """배치 작업 삭제"""
    job = db.session.get(BatchJob, job_id)
    if not job:
        abort(404)
    
    db.session.delete(job)
    db.session.commit()
    
    flash('배치 작업이 삭제되었습니다.', 'success')
    return redirect(url_for('jobs'))

@app.route('/jobs/<int:job_id>/execute', methods=['POST'])
def execute_job(job_id):
    """배치 작업 실행"""
    job = db.session.get(BatchJob, job_id)
    if not job:
        abort(404)
    
    executor = BatchExecutor()
    success = executor.execute_job(job_id)
    
    if success:
        flash('배치 작업이 성공적으로 실행되었습니다.', 'success')
    else:
        flash('배치 작업 실행 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('jobs'))

@app.route('/schedules')
def schedules():
    """스케줄 관리 페이지"""
    schedules = db.session.query(BatchSchedule).all()
    jobs = db.session.query(BatchJob).filter_by(is_active=True).all()
    
    # 스케줄러 등록 상태 확인
    scheduler_jobs = scheduler.get_jobs()
    scheduler_job_ids = {job.id for job in scheduler_jobs}
    
    for schedule in schedules:
        schedule.scheduler_registered = f'schedule_{schedule.id}' in scheduler_job_ids
        
        # 스케줄러의 실제 next_run_time 가져오기 (이미 KST)
        scheduler_next_run = get_scheduler_next_run_time(schedule.id)
        if scheduler_next_run:
            schedule.scheduler_next_run = format_scheduler_time(scheduler_next_run, '%m-%d %H:%M')
            schedule.scheduler_next_run_year = format_scheduler_time(scheduler_next_run, '%Y')
        else:
            # 스케줄러에 등록되지 않은 경우 DB의 시간 사용 (이미 KST)
            if schedule.next_run:
                schedule.scheduler_next_run = format_db_kst_time(schedule.next_run, '%m-%d %H:%M')
                schedule.scheduler_next_run_year = format_db_kst_time(schedule.next_run, '%Y')
            else:
                schedule.scheduler_next_run = None
                schedule.scheduler_next_run_year = None
    
    return render_template('schedules.html', schedules=schedules, jobs=jobs)

@app.route('/schedules/add', methods=['GET', 'POST'])
def add_schedule():
    """스케줄 추가"""
    if request.method == 'POST':
        data = request.form
        
        print(f"=== 스케줄 추가 요청 ===")
        print(f"job_id: {data.get('job_id')}")
        print(f"cron_expression: {data.get('cron_expression')}")
        
        schedule = BatchSchedule(
            job_id=int(data['job_id']),
            cron_expression=data['cron_expression'],
            is_active=True  # 기본적으로 활성화
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        print(f"스케줄 ID: {schedule.id}")
        
        # 스케줄러에 작업 추가
        job = db.session.query(BatchJob).get(schedule.job_id)
        if job:
            try:
                # 기존 작업이 있다면 제거
                try:
                    scheduler.remove_job(f'schedule_{schedule.id}')
                except:
                    pass
                
                # 새 작업 추가
                scheduler.add_job(
                    func=execute_scheduled_job,
                    trigger=CronTrigger.from_crontab(schedule.cron_expression),
                    args=[schedule.id],
                    id=f'schedule_{schedule.id}',
                    replace_existing=True
                )
                
                # 다음 실행 시간을 DB에 저장 (스케줄러는 이미 KST)
                scheduler_next_run = get_scheduler_next_run_time(schedule.id)
                if scheduler_next_run:
                    # 스케줄러는 이미 Asia/Seoul 시간대이므로 직접 저장
                    schedule.next_run = scheduler_next_run
                    db.session.commit()
                
                print(f"스케줄러에 작업 등록 성공: schedule_{schedule.id}")
                print(f"다음 실행 시간: {schedule.next_run}")
                
            except Exception as e:
                print(f"스케줄러 등록 실패: {e}")
                # 스케줄러 등록 실패 시 비활성화
                schedule.is_active = False
                db.session.commit()
                flash(f'스케줄이 추가되었지만 스케줄러 등록에 실패했습니다: {e}', 'warning')
                return redirect(url_for('schedules'))
        else:
            print(f"배치 작업을 찾을 수 없음: {schedule.job_id}")
            flash('배치 작업을 찾을 수 없습니다.', 'error')
            return redirect(url_for('schedules'))
        
        flash('스케줄이 추가되었습니다.', 'success')
        return redirect(url_for('schedules'))
    
    # GET 요청은 schedules 페이지로 리다이렉트 (폼이 schedules.html에 있음)
    return redirect(url_for('schedules'))

@app.route('/schedules/<int:schedule_id>/edit', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    """스케줄 수정"""
    schedule = db.session.query(BatchSchedule).get_or_404(schedule_id)
    
    if request.method == 'POST':
        data = request.form
        
        print(f"=== 스케줄 수정 요청 ===")
        print(f"schedule_id: {schedule_id}")
        print(f"cron_expression: {data.get('cron_expression')}")
        print(f"is_active: {'is_active' in data}")
        
        schedule.cron_expression = data['cron_expression']
        schedule.is_active = 'is_active' in data
        
        db.session.commit()
        
        # 스케줄러 업데이트
        try:
            # 기존 작업 제거
            try:
                scheduler.remove_job(f'schedule_{schedule.id}')
            except:
                pass
            
            if schedule.is_active:
                # 새 작업 추가
                scheduler.add_job(
                    func=execute_scheduled_job,
                    trigger=CronTrigger.from_crontab(schedule.cron_expression),
                    args=[schedule.id],
                    id=f'schedule_{schedule.id}',
                    replace_existing=True
                )
                
                # 다음 실행 시간 업데이트
                try:
                    scheduler_next_run = get_scheduler_next_run_time(schedule.id)
                    if scheduler_next_run:
                        # 스케줄러는 이미 Asia/Seoul 시간대이므로 직접 저장
                        schedule.next_run = scheduler_next_run
                except:
                    pass
                
                print(f"스케줄러에 작업 등록 성공: schedule_{schedule.id}")
                print(f"다음 실행 시간: {schedule.next_run}")
            else:
                # 비활성화 시 next_run 초기화
                schedule.next_run = None
                db.session.commit()
                print(f"스케줄 비활성화: schedule_{schedule.id}")
                
        except Exception as e:
            print(f"스케줄러 업데이트 실패: {e}")
            # 스케줄러 등록 실패 시 비활성화
            schedule.is_active = False
            schedule.next_run = None
            db.session.commit()
            flash(f'스케줄이 수정되었지만 스케줄러 업데이트에 실패했습니다: {e}', 'warning')
            return redirect(url_for('schedules'))
        
        flash('스케줄이 수정되었습니다.', 'success')
        return redirect(url_for('schedules'))
    
    # GET 요청은 schedules 페이지로 리다이렉트 (폼이 schedules.html에 있음)
    return redirect(url_for('schedules'))

@app.route('/schedules/<int:schedule_id>/delete', methods=['POST'])
def delete_schedule(schedule_id):
    """스케줄 삭제"""
    schedule = db.session.query(BatchSchedule).get_or_404(schedule_id)
    
    # 스케줄러에서 제거
    scheduler.remove_job(f'schedule_{schedule.id}')
    
    db.session.delete(schedule)
    db.session.commit()
    
    flash('스케줄이 삭제되었습니다.', 'success')
    return redirect(url_for('schedules'))

def execute_scheduled_job(schedule_id):
    """스케줄된 작업 실행"""
    with app.app_context():
        try:
            schedule = db.session.query(BatchSchedule).get(schedule_id)
            if not schedule:
                print(f"❌ 스케줄을 찾을 수 없음: schedule_id={schedule_id}")
                return
            
            if not schedule.is_active:
                print(f"⚠️ 스케줄이 비활성화됨: schedule_id={schedule_id}")
                return
            
            print(f"🔄 스케줄 실행 시작: schedule_id={schedule_id}, job_id={schedule.job_id}")
            
            # 실행 로그 생성 - 명시적으로 KST 시간 사용
            started_at = get_kst_now()
            log = BatchLog(
                job_id=schedule.job_id,
                schedule_id=schedule.id,
                status='running',
                started_at=started_at
            )
            db.session.add(log)
            db.session.commit()
            
            # 작업 실행
            executor = BatchExecutor()
            success = executor.execute_job(schedule.job_id)
            
            # 로그 업데이트 - 명시적으로 KST 시간 사용
            completed_at = get_kst_now()
            log.completed_at = completed_at
            log.status = 'success' if success else 'failed'
            
            # 시간대 안전한 소요 시간 계산
            try:
                # 두 시간 모두 KST 시간대이므로 직접 계산 가능
                log.duration_seconds = (completed_at - started_at).total_seconds()
            except Exception as e:
                print(f"⚠️ 소요 시간 계산 실패: {e}")
                log.duration_seconds = None
            
            # 스케줄 정보 업데이트 - 명시적으로 KST 시간 사용
            schedule.last_run = get_kst_now()
            
            # 다음 실행 시간 업데이트
            try:
                scheduler_job = scheduler.get_job(f'schedule_{schedule.id}')
                if scheduler_job and scheduler_job.next_run_time:
                    # 스케줄러는 이미 Asia/Seoul 시간대이므로 직접 저장
                    schedule.next_run = scheduler_job.next_run_time
            except Exception as e:
                print(f"⚠️ 다음 실행 시간 업데이트 실패: {e}")
            
            db.session.commit()
            
            print(f"✅ 스케줄 실행 완료: schedule_id={schedule_id}, success={success}")
            
        except Exception as e:
            print(f"❌ 스케줄 실행 중 오류 발생: schedule_id={schedule_id}, error={e}")
            
            # 오류 로그 기록 - 명시적으로 KST 시간 사용
            try:
                log = BatchLog(
                    job_id=schedule.job_id if 'schedule' in locals() else None,
                    schedule_id=schedule_id,
                    status='failed',
                    started_at=get_kst_now(),
                    completed_at=get_kst_now(),
                    error_message=str(e)
                )
                db.session.add(log)
                db.session.commit()
            except:
                pass

@app.route('/logs')
def logs():
    """로그 조회 페이지"""
    page = request.args.get('page', 1, type=int)
    logs = db.session.query(BatchLog).order_by(BatchLog.started_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('logs.html', logs=logs)

@app.route('/api/test-connection/<server_name>', methods=['POST'])
def test_connection(server_name):
    """서버 연결 테스트"""
    try:
        # 로그 디렉토리 생성
        log_dir = "/app/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "db_connection.log")
        
        # 로그 기록
        import logging
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        
        # 설정 파일 동기화
        config_manager = ConfigManager()
        config_manager.sync_from_database()
        
        # 연결 테스트 (원래 db_query.py의 함수들 사용)
        logging.info(f"=== {server_name} 연결 테스트 시작 ===")
        
        # 작업 디렉토리를 db_connection_test로 변경
        original_cwd = os.getcwd()
        os.chdir('/app/db_connection_test')
        
        try:
            conf = get_server_config(server_name)
            db_type = conf['type']
            
            logging.info(f"서버 정보: {db_type}://{conf['host']}:{conf['port']}/{conf['database']}")
            
            # 간단한 테스트 쿼리
            if db_type == 'postgresql':
                test_query = "SELECT 1 as test"
            elif db_type == 'altibase':
                test_query = "SELECT 1 FROM DUAL"
            elif db_type == 'informix':
                test_query = "SELECT 1 FROM DUAL" # Informix는 간단한 쿼리로 테스트
            else:
                test_query = "SELECT 1 FROM DUAL" # 기본 쿼리
            
            logging.info(f"테스트 쿼리: {test_query}")
            
            if db_type == 'altibase':
                result, success, error = test_altibase_connection(conf, test_query)
            elif db_type == 'informix':
                result, success, error = test_informix_connection(conf, test_query)
            else:
                result, success, error = db_execute_query(server_name, test_query)
            
            if success:
                logging.info(f"✅ {server_name} ({db_type}) 연결 성공")
                logging.info(f"테스트 결과: {result}")
                return jsonify({
                    "success": True,
                    "message": f"{db_type} 연결 성공",
                    "test_result": result
                })
            else:
                logging.error(f"❌ {server_name} ({db_type}) 연결 실패")
                logging.error(f"오류: {error}")
                return jsonify({
                    "success": False,
                    "error": error
                })
        finally:
            # 작업 디렉토리 복원
            os.chdir(original_cwd)
        
    except Exception as e:
        logging.error(f"❌ {server_name} 연결 테스트 중 예외 발생: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/logs')
def api_logs():
    """로그 API"""
    page = request.args.get('page', 1, type=int)
    logs = db.session.query(BatchLog).order_by(BatchLog.started_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'job_name': log.job.name,
            'status': log.status,
            'total_rows': log.total_rows,
            'duration_seconds': log.duration_seconds,
            'started_at': format_kst_time(log.started_at) if log.started_at else None,
            'completed_at': format_kst_time(log.completed_at) if log.completed_at else None,
            'error_message': log.error_message
        } for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })

@app.route('/api/db-logs')
def api_db_logs():
    """데이터베이스 연결 로그 API"""
    try:
        log_file_path = "/app/logs/db_connection.log"
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                # 마지막 50줄만 읽기
                lines = f.readlines()
                recent_logs = lines[-50:] if len(lines) > 50 else lines
                return jsonify({
                    'success': True,
                    'logs': recent_logs,
                    'total_lines': len(lines)
                })
        else:
            return jsonify({
                'success': False,
                'error': '로그 파일이 존재하지 않습니다.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/diagnose-jar/<jar_name>')
def diagnose_jar(jar_name):
    """JAR 파일 진단 API (원래 기능에는 없음)"""
    return jsonify({
        'success': False,
        'error': 'JAR 진단 기능은 원래 db_query.py에 없데 기능입니다.'
    })

@app.route('/api/scheduler-status')
def api_scheduler_status():
    """스케줄러 상태 확인 API"""
    try:
        jobs = scheduler.get_jobs()
        job_list = []
        
        for job in jobs:
            # 다음 실행 시간을 KST로 변환 (스케줄러는 이미 KST)
            next_run_kst = None
            if job.next_run_time:
                next_run_kst = format_scheduler_time(job.next_run_time, '%Y-%m-%d %H:%M:%S')
            
            job_info = {
                'id': job.id,
                'name': job.name,
                'func': str(job.func),
                'trigger': str(job.trigger),
                'next_run_time': next_run_kst,
                'next_run_original': str(job.next_run_time) if job.next_run_time else None,  # 디버깅용
                'next_run_relative': _get_relative_time(job.next_run_time) if job.next_run_time else None
            }
            job_list.append(job_info)
        
        # 데이터베이스의 스케줄 정보와 매칭
        db_schedules = db.session.query(BatchSchedule).all()
        schedule_status = []
        
        for db_schedule in db_schedules:
            # 스케줄러에서 해당 작업 찾기
            scheduler_job = None
            for job in jobs:
                if job.id == f'schedule_{db_schedule.id}':
                    scheduler_job = job
                    break
            
            # 스케줄러의 다음 실행 시간을 KST로 변환 (스케줄러는 이미 KST)
            next_run_from_scheduler = None
            if scheduler_job and scheduler_job.next_run_time:
                next_run_from_scheduler = format_scheduler_time(scheduler_job.next_run_time, '%Y-%m-%d %H:%M:%S')
            
            schedule_info = {
                'id': db_schedule.id,
                'job_id': db_schedule.job_id,
                'job_name': db_schedule.job.name if db_schedule.job else 'Unknown',
                'cron_expression': db_schedule.cron_expression,
                'is_active': db_schedule.is_active,
                'last_run': format_kst_time(db_schedule.last_run) if db_schedule.last_run else None,
                'created_at': format_kst_time(db_schedule.created_at),
                'scheduler_registered': scheduler_job is not None,
                'next_run_from_db': format_db_kst_time(db_schedule.next_run, '%Y-%m-%d %H:%M:%S') if db_schedule.next_run else None,  # DB는 이미 KST
                'next_run_from_scheduler': next_run_from_scheduler,
                'next_run_original': str(scheduler_job.next_run_time) if scheduler_job and scheduler_job.next_run_time else None,
                # 스케줄 목록에서 사용할 다음 실행 시간 (스케줄러 우선, DB 백업)
                'next_run_display': next_run_from_scheduler or (format_db_kst_time(db_schedule.next_run, '%Y-%m-%d %H:%M:%S') if db_schedule.next_run else None)
            }
            schedule_status.append(schedule_info)
        
        return jsonify({
            'success': True,
            'scheduler_running': scheduler.running,
            'total_jobs': len(jobs),
            'total_schedules': len(db_schedules),
            'active_schedules': len([s for s in db_schedules if s.is_active]),
            'jobs': job_list,
            'schedules': schedule_status,
            'current_time': format_kst_time(get_kst_now())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def _get_relative_time(dt):
    """상대적 시간 표시 (예: 5분 후, 2시간 후)"""
    if not dt:
        return None
    
    now = get_kst_now()
    # 스케줄러는 이미 KST 시간대이므로 tzinfo가 없으면 KST로 설정
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST)
    
    diff = dt - now
    
    if diff.total_seconds() < 0:
        return "이미 지남"
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}일 {hours}시간 후"
    elif hours > 0:
        return f"{hours}시간 {minutes}분 후"
    elif minutes > 0:
        return f"{minutes}분 후"
    else:
        return "곧 실행"

@app.route('/api/test-schedule/<int:schedule_id>')
def api_test_schedule(schedule_id):
    """스케줄 테스트 실행 API"""
    try:
        schedule = db.session.query(BatchSchedule).get_or_404(schedule_id)
        
        # 스케줄된 작업 실행
        executor = BatchExecutor()
        success = executor.execute_job(schedule.job_id)
        
        # 스케줄 정보 업데이트
        schedule.last_run = get_kst_now()
        
        # 다음 실행 시간 업데이트
        try:
            scheduler_job = scheduler.get_job(f'schedule_{schedule.id}')
            if scheduler_job and scheduler_job.next_run_time:
                schedule.next_run = scheduler_job.next_run_time
        except:
            pass
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '스케줄 테스트 실행 완료',
            'schedule_id': schedule_id,
            'job_id': schedule.job_id,
            'execution_success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/restore-schedules', methods=['POST'])
def api_restore_schedules():
    """스케줄 복원 API"""
    try:
        restored_count, failed_count = restore_schedules_from_database()
        
        return jsonify({
            'success': True,
            'message': f'스케줄 복원 완료: 성공 {restored_count}개, 실패 {failed_count}개',
            'restored_count': restored_count,
            'failed_count': failed_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_scheduler_next_run_time(schedule_id):
    """스케줄러에서 다음 실행 시간을 KST로 가져오기"""
    try:
        scheduler_job = scheduler.get_job(f'schedule_{schedule_id}')
        if scheduler_job and scheduler_job.next_run_time:
            # 스케줄러는 이미 Asia/Seoul 시간대로 설정되어 있으므로 직접 사용
            return scheduler_job.next_run_time
        return None
    except Exception as e:
        print(f"스케줄러에서 다음 실행 시간 가져오기 실패: {e}")
        return None

def format_scheduler_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """스케줄러 시간을 포맷팅 (이미 KST이므로 변환 없이 포맷팅만)"""
    if dt is None:
        return '-'
    return dt.strftime(format_str)

def restore_schedules_from_database():
    """데이터베이스의 활성 스케줄을 스케줄러에 복원"""
    try:
        print("🔄 데이터베이스에서 스케줄 복원 중...")
        
        # 활성 스케줄 조회
        active_schedules = db.session.query(BatchSchedule).filter_by(is_active=True).all()
        
        restored_count = 0
        failed_count = 0
        
        for schedule in active_schedules:
            try:
                # 기존 작업이 있다면 제거
                try:
                    scheduler.remove_job(f'schedule_{schedule.id}')
                except:
                    pass
                
                # 새 작업 추가
                scheduler.add_job(
                    func=execute_scheduled_job,
                    trigger=CronTrigger.from_crontab(schedule.cron_expression),
                    args=[schedule.id],
                    id=f'schedule_{schedule.id}',
                    replace_existing=True
                )
                
                # 다음 실행 시간 업데이트 - 명시적으로 KST 시간 사용
                scheduler_next_run = get_scheduler_next_run_time(schedule.id)
                if scheduler_next_run:
                    # 스케줄러에서 가져온 시간이 이미 KST이므로 직접 저장
                    schedule.next_run = scheduler_next_run
                
                restored_count += 1
                print(f"✅ 스케줄 복원 성공: schedule_{schedule.id} ({schedule.cron_expression})")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ 스케줄 복원 실패: schedule_{schedule.id} - {e}")
                # 복원 실패 시 비활성화
                schedule.is_active = False
                schedule.next_run = None
        
        # 변경사항 저장
        db.session.commit()
        
        print(f"📊 스케줄 복원 완료: 성공 {restored_count}개, 실패 {failed_count}개")
        return restored_count, failed_count
        
    except Exception as e:
        print(f"❌ 스케줄 복원 중 오류 발생: {e}")
        # 오류 발생 시 롤백
        db.session.rollback()
        return 0, 0

# 초기화 함수
def init_app():
    """애플리케이션 초기화"""
    with app.app_context():
        # 데이터베이스 생성
        db.create_all()
        
        # 설정 파일에서 데이터베이스로 동기화
        config_manager = ConfigManager()
        config_manager.sync_to_database()
        
        # 기본 서버 설정 (로컬 PostgreSQL)
        if not db.session.query(ServerConfig).filter_by(name='local_pgsql').first():
            local_server = ServerConfig(
                name='local_pgsql',
                type='postgresql',
                host='postgres',  # Docker 컨테이너 이름
                port=5432,
                database='fs_master_web',
                user='postgres',
                password=os.environ.get('POSTGRES_PASSWORD')
            )
            db.session.add(local_server)
            db.session.commit()
        
        # 데이터베이스의 활성 스케줄을 스케줄러에 복원
        try:
            print("🔄 데이터베이스에서 스케줄 복원 중...")
            restored_count, failed_count = restore_schedules_from_database()
            print(f"✅ 스케줄 복원 완료: 성공 {restored_count}개, 실패 {failed_count}개")
        except Exception as e:
            print(f"⚠️ 스케줄 복원 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

def setup_only():
    """설정 전용 모드"""
    print("🗃️ 데이터베이스 테이블 생성 중...")
    init_app()
    print("✅ 데이터베이스 테이블 생성 완료")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='FS Master Web Application')
    parser.add_argument('--setup-only', action='store_true', 
                       help='데이터베이스 테이블만 생성하고 종료')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='서버 호스트 (기본값: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='서버 포트 (기본값: 5000)')
    parser.add_argument('--debug', action='store_true', default=True,
                       help='디버그 모드 활성화')
    
    args = parser.parse_args()
    
    if args.setup_only:
        setup_only()
        return
    
    print("🚀 FS Master Web Application 시작")
    print(f"📍 서버 주소: http://{args.host}:{args.port}")
    print(f"🗄️ 데이터베이스: {database_url}")
    
    # PostgreSQL 연결 대기
    if not wait_for_postgres():
        print("❌ PostgreSQL 연결 실패로 애플리케이션을 종료합니다.")
        return
    
    # 애플리케이션 초기화
    init_app()
    
    # 웹 서버 시작 (개발 모드에서 자동 리로드 활성화)
    app.run(debug=True, host=args.host, port=args.port, use_reloader=True)

@app.route('/api/debug-scheduler')
def api_debug_scheduler():
    """스케줄러 디버깅 정보 API"""
    try:
        # 현재 시간
        now_kst = get_kst_now()
        
        # 스케줄러 상태
        scheduler_jobs = scheduler.get_jobs()
        
        # 데이터베이스 스케줄 정보
        db_schedules = db.session.query(BatchSchedule).all()
        
        debug_info = {
            'current_time_kst': now_kst.strftime('%Y-%m-%d %H:%M:%S'),
            'scheduler_timezone': str(scheduler.timezone),
            'scheduler_running': scheduler.running,
            'total_scheduler_jobs': len(scheduler_jobs),
            'scheduler_jobs': []
        }
        
        # 스케줄러 작업 정보
        for job in scheduler_jobs:
            job_info = {
                'id': job.id,
                'func': str(job.func),
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time) if job.next_run_time else None,
                'next_run_time_kst': format_scheduler_time(job.next_run_time) if job.next_run_time else None
            }
            debug_info['scheduler_jobs'].append(job_info)
        
        # 데이터베이스 스케줄 정보
        debug_info['db_schedules'] = []
        for schedule in db_schedules:
            schedule_info = {
                'id': schedule.id,
                'job_id': schedule.job_id,
                'cron_expression': schedule.cron_expression,
                'is_active': schedule.is_active,
                'last_run': format_db_kst_time(schedule.last_run) if schedule.last_run else None,
                'next_run': format_db_kst_time(schedule.next_run) if schedule.next_run else None,
                'scheduler_registered': f'schedule_{schedule.id}' in [job.id for job in scheduler_jobs]
            }
            debug_info['db_schedules'].append(schedule_info)
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/schedule-logs')
def api_schedule_logs():
    """스케줄 실행 로그 API"""
    try:
        # 최근 24시간 동안의 스케줄 관련 로그
        yesterday = get_kst_now() - timedelta(days=1)
        
        logs = db.session.query(BatchLog).filter(
            BatchLog.schedule_id.isnot(None),
            BatchLog.started_at >= yesterday
        ).order_by(BatchLog.started_at.desc()).all()
        
        log_list = []
        for log in logs:
            log_info = {
                'id': log.id,
                'schedule_id': log.schedule_id,
                'job_id': log.job_id,
                'status': log.status,
                'started_at': format_db_kst_time(log.started_at) if log.started_at else None,
                'completed_at': format_db_kst_time(log.completed_at) if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'total_rows': log.total_rows,
                'error_message': log.error_message
            }
            log_list.append(log_info)
        
        return jsonify({
            'success': True,
            'logs': log_list,
            'total_count': len(log_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/debug-timezone')
def api_debug_timezone():
    """시간대 디버깅 API"""
    try:
        from datetime import datetime, timezone, timedelta
        
        # 현재 시간들
        utc_now = datetime.now(timezone.utc)
        kst_now = get_kst_now()
        local_now = datetime.now()
        
        # 스케줄러 정보
        scheduler_info = {
            'timezone': str(scheduler.timezone),
            'running': scheduler.running,
            'job_count': len(scheduler.get_jobs())
        }
        
        # 활성 스케줄들의 시간 정보
        active_schedules = db.session.query(BatchSchedule).filter_by(is_active=True).all()
        schedule_times = []
        
        for schedule in active_schedules:
            try:
                scheduler_job = scheduler.get_job(f'schedule_{schedule.id}')
                schedule_info = {
                    'id': schedule.id,
                    'cron_expression': schedule.cron_expression,
                    'db_last_run': format_db_kst_time(schedule.last_run) if schedule.last_run else None,
                    'db_next_run': format_db_kst_time(schedule.next_run) if schedule.next_run else None,
                    'scheduler_next_run': format_scheduler_time(scheduler_job.next_run_time) if scheduler_job and scheduler_job.next_run_time else None
                }
                schedule_times.append(schedule_info)
            except Exception as e:
                schedule_times.append({
                    'id': schedule.id,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'current_times': {
                'utc': utc_now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'kst': kst_now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'local': local_now.strftime('%Y-%m-%d %H:%M:%S')
            },
            'scheduler_info': scheduler_info,
            'schedule_times': schedule_times
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    main() 