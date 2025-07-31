import jaydebeapi
import psycopg2
import configparser
import sys

def get_server_config(server_name):
    """서버 설정 정보 가져오기"""
    config = configparser.ConfigParser()
    config.read('db_servers.ini')
    if server_name not in config:
        raise Exception(f"서버 '{server_name}' 설정이 없습니다.")
    section = config[server_name]
    return {
        "type": section["type"],
        "host": section["host"],
        "port": section["port"],
        "database": section["database"],
        "user": section["user"],
        "password": section["password"]
    }

def connect_informix(conf):
    """Informix 데이터베이스 연결"""
    url = f"jdbc:informix-sqli://{conf['host']}:{conf['port']}/{conf['database']}:NEWCODESET=EUC-KR,cp1252,819"
    driver = "com.informix.jdbc.IfxDriver"
    jar = "ifxjdbc.jar"
    return jaydebeapi.connect(driver, url, [conf['user'], conf['password']], jar)

def connect_altibase(conf):
    """Altibase 데이터베이스 연결"""
    driver = "Altibase.jdbc.driver.AltibaseDriver"
    url = f"jdbc:Altibase://{conf['host']}:{conf['port']}/{conf['database']}"
    jar = "Altibase.jar"
    
    conn = jaydebeapi.connect(driver, url, [conf['user'], conf['password']], jar)
    conn.autocommit = False
    return conn

def connect_postgresql(conf):
    """PostgreSQL 데이터베이스 연결"""
    conn_string = f"host={conf['host']} port={conf['port']} dbname={conf['database']} user={conf['user']} password={conf['password']}"
    return psycopg2.connect(conn_string)

def convert_java_to_python(value):
    """Java 객체를 Python 객체로 변환"""
    if value is None:
        return None
    
    # java.math.BigDecimal -> Python float/int
    if hasattr(value, 'doubleValue'):
        try:
            str_val = str(value)
            if '.' in str_val:
                double_val = value.doubleValue()
                return int(double_val) if double_val.is_integer() else double_val
            else:
                return int(str_val)
        except:
            return float(str(value))
    
    # java.lang.String -> Python str
    elif hasattr(value, 'toString'):
        return str(value)
    
    # java.lang.Integer/Long -> Python int
    elif hasattr(value, 'intValue'):
        return int(value)
    elif hasattr(value, 'longValue'):
        return int(value)
    
    # PostgreSQL Decimal -> Python float
    elif str(type(value)).startswith("<class 'decimal.Decimal'>"):
        return float(value)
    
    # 기타 Java 객체는 문자열로 변환
    elif str(type(value)).startswith("<java object"):
        return str(value)
    
    return value

def execute_query(server_name, query):
    """서버에 연결하여 쿼리 실행"""
    conf = get_server_config(server_name)
    db_type = conf['type']
    
    try:
        # 데이터베이스 연결
        if db_type == 'informix':
            conn = connect_informix(conf)
        elif db_type == 'altibase':
            conn = connect_altibase(conf)
        elif db_type == 'postgresql':
            conn = connect_postgresql(conf)
        else:
            return None, False, f"지원하지 않는 데이터베이스 타입: {db_type}"
        
        # Altibase의 경우 Java 레벨에서 직접 접근
        if db_type == 'altibase':
            try:
                java_conn = conn.jconn
                java_stmt = java_conn.createStatement()
                java_stmt.setQueryTimeout(30)
                java_result_set = java_stmt.executeQuery(query)
                
                # 결과 가져오기
                rows = []
                while java_result_set.next():
                    meta_data = java_result_set.getMetaData()
                    column_count = meta_data.getColumnCount()
                    
                    row = []
                    for i in range(1, column_count + 1):
                        value = java_result_set.getObject(i)
                        row.append(convert_java_to_python(value))
                    
                    rows.append(tuple(row))
                
                # 자원 반납
                java_result_set.close()
                java_stmt.close()
                conn.close()
                return rows, True, None
                
            except Exception as e:
                java_stmt.close()
                conn.close()
                return None, False, str(e)
        
        # PostgreSQL과 Informix는 일반 방식
        else:
            curs = conn.cursor()
            curs.execute(query)
            rows = curs.fetchall()
            curs.close()
            conn.close()
            return rows, True, None
            
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return None, False, error_msg

def list_servers():
    """사용 가능한 서버 목록 출력"""
    config = configparser.ConfigParser()
    config.read('db_servers.ini')
    
    print("=" * 60)
    print("연결 가능한 서버 목록")
    print("=" * 60)
    
    servers = []
    for i, server_name in enumerate(config.sections(), 1):
        server_type = config[server_name]['type']
        host = config[server_name]['host']
        port = config[server_name]['port']
        database = config[server_name]['database']
        print(f"{i:2d}. {server_name:<15} ({server_type}) - {host}:{port}/{database}")
        servers.append(server_name)
    
    print("=" * 60)
    return servers

def get_user_input(prompt, allow_empty=False):
    """사용자 입력 받기"""
    while True:
        try:
            user_input = input(prompt).strip()
            if allow_empty or user_input:
                return user_input
            else:
                print("입력이 필요합니다. 다시 입력해주세요.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            sys.exit(0)
        except EOFError:
            print("\n프로그램을 종료합니다.")
            sys.exit(0)

def get_multiline_query():
    """여러 줄 쿼리 입력 받기"""
    print("\n쿼리를 입력하세요 (입력 완료 후 빈 줄에서 Enter):")
    print("-" * 50)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\n쿼리 입력을 취소합니다.")
            return None
        except EOFError:
            print("\n프로그램을 종료합니다.")
            sys.exit(0)
    
    return "\n".join(lines)

def interactive_mode():
    """인터랙티브 모드"""
    print("데이터베이스 쿼리 실행기")
    print("=" * 60)
    
    servers = list_servers()
    if not servers:
        print("사용 가능한 서버가 없습니다.")
        return
    
    while True:
        # 서버 선택
        server_choice = get_user_input(f"\n서버를 선택하세요 (1-{len(servers)}) 또는 'q'로 종료: ")
        
        if server_choice.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        try:
            server_index = int(server_choice) - 1
            if 0 <= server_index < len(servers):
                selected_server = servers[server_index]
            else:
                print(f"1-{len(servers)} 사이의 숫자를 입력하세요.")
                continue
        except ValueError:
            print("올바른 숫자를 입력하세요.")
            continue
        
        # 쿼리 입력
        query = get_multiline_query()
        if query is None or not query.strip():
            print("쿼리가 비어있습니다.")
            continue
        
        # 쿼리 실행
        print(f"\n선택된 서버: {selected_server}")
        print("쿼리 실행 중...")
        rows, success, error = execute_query(selected_server, query)
        
        if success:
            if rows:
                print(f"\n쿼리 결과 ({len(rows)}개 행):")
                print("-" * 50)
                for i, row in enumerate(rows, 1):
                    print(f"{i:3d}. {row}")
            else:
                print("\n쿼리 실행 완료 (결과 없음)")
        else:
            print(f"\n오류 발생: {error}")
        
        # 계속할지 묻기
        continue_choice = get_user_input("\n다른 쿼리를 실행하시겠습니까? (y/n): ")
        if continue_choice.lower() not in ['y', 'yes', 'ㅇ']:
            print("프로그램을 종료합니다.")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 명령행 인자로 서버명이 주어진 경우
        server_name = sys.argv[1]
        if len(sys.argv) > 2:
            # 쿼리도 명령행에서 제공된 경우
            query = " ".join(sys.argv[2:])
            rows, success, error = execute_query(server_name, query)
            if success:
                if rows:
                    print(f"\n쿼리 결과 ({len(rows)}개 행):")
                    print("-" * 50)
                    for i, row in enumerate(rows, 1):
                        print(f"{i:3d}. {row}")
                else:
                    print("\n쿼리 실행 완료 (결과 없음)")
            else:
                print(f"\n오류 발생: {error}")
        else:
            # 쿼리만 입력받는 경우
            query = get_multiline_query()
            if query:
                rows, success, error = execute_query(server_name, query)
                if success:
                    if rows:
                        print(f"\n쿼리 결과 ({len(rows)}개 행):")
                        print("-" * 50)
                        for i, row in enumerate(rows, 1):
                            print(f"{i:3d}. {row}")
                    else:
                        print("\n쿼리 실행 완료 (결과 없음)")
                else:
                    print(f"\n오류 발생: {error}")
    else:
        # 인터랙티브 모드
        interactive_mode() 