"""
FS Master Migration Tool

db_connection_test를 import하여 사용하는 마이그레이션 도구
"""

import db_connection_test
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

class FSMigrationTool:
    """FS Master 마이그레이션 도구"""
    
    def __init__(self, config_file: str = 'db_connection_test/db_servers.ini'):
        self.config_file = config_file
        self.db_connector = db_connection_test.SimpleDatabaseConnector(config_file)
        
    def show_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*60)
        print("🚀 FS Master 데이터 마이그레이션 도구")
        print("="*60)
        print("1. 데이터베이스 연결 테스트")
        print("2. FS1 → 로컬 PostgreSQL 마이그레이션")
        print("3. FS1 → 클라우드 PostgreSQL 마이그레이션")
        print("4. 쿼리 실행")
        print("5. 테이블 최적화")
        print("6. 설정 파일 관리")
        print("7. 배치 마이그레이션")
        print("0. 종료")
        print("="*60)
    
    def test_connections(self):
        """데이터베이스 연결 테스트"""
        print("\n🔍 데이터베이스 연결 테스트")
        print("-" * 40)
        
        try:
            servers = self.db_connector.get_server_list()
            
            if not servers:
                print("❌ 설정된 서버가 없습니다.")
                return
            
            print(f"발견된 서버: {len(servers)}개")
            
            for i, server in enumerate(servers, 1):
                print(f"\n{i}. {server}")
                try:
                    info = self.db_connector.get_server_info(server)
                    print(f"   타입: {info['type']}")
                    print(f"   호스트: {info['host']}:{info['port']}")
                    print(f"   데이터베이스: {info['database']}")
                    print(f"   사용자: {info['user']}")
                    
                    # 연결 테스트
                    if info['type'] == 'postgresql':
                        engine = self.db_connector.create_engine(server)
                        with engine.connect() as conn:
                            result = conn.execute("SELECT 1 as test")
                            print(f"   ✅ 연결 성공")
                        engine.dispose()
                    else:
                        # Informix, Altibase 연결 테스트
                        conn = self.db_connector.connect(server)
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        print(f"   ✅ 연결 성공")
                        cursor.close()
                    
                except Exception as e:
                    print(f"   ❌ 연결 실패: {e}")
            
        except Exception as e:
            print(f"❌ 연결 테스트 실패: {e}")
    
    def migrate_to_local_pgsql(self):
        """FS1에서 로컬 PostgreSQL로 마이그레이션"""
        print("\n⚡ FS1 → 로컬 PostgreSQL 마이그레이션")
        print("-" * 50)
        
        try:
            # 소스 서버 (FS1)
            source_server = 'FS1'
            
            # 타겟 서버 (로컬 PostgreSQL)
            target_server = 'local_pgsql'
            
            # 쿼리 입력
            print("\n📝 소스 데이터 쿼리를 입력하세요:")
            print("(예: SELECT * FROM fds_팩셋.\"인포맥스종목마스터\")")
            query = self._get_multiline_input()
            
            if not query:
                print("❌ 쿼리가 입력되지 않았습니다.")
                return
            
            # 타겟 테이블명 입력
            target_table = input("\n📋 타겟 테이블명을 입력하세요: ").strip()
            if not target_table:
                print("❌ 테이블명이 입력되지 않았습니다.")
                return
            
            # 마이그레이션 방식 선택
            print("\n🚀 마이그레이션 방식을 선택하세요:")
            print("1. 스트리밍 마이그레이션 (안정적)")
            print("2. 병렬 마이그레이션 (고성능)")
            
            try:
                choice = int(input("선택 (1-2): "))
                
                if choice == 1:
                    # 스트리밍 마이그레이션
                    chunk_size = self._get_chunk_size()
                    print(f"\n🚀 스트리밍 마이그레이션 시작...")
                    print(f"소스: {source_server}")
                    print(f"타겟: {target_server}")
                    print(f"테이블: {target_table}")
                    print(f"청크 크기: {chunk_size:,}")
                    
                    start_time = time.time()
                    result = self.db_connector.stream_data(
                        source_server, query, target_server, target_table, chunk_size
                    )
                    end_time = time.time()
                    
                elif choice == 2:
                    # 병렬 마이그레이션
                    num_workers = self._get_worker_count()
                    print(f"\n🚀 병렬 마이그레이션 시작...")
                    print(f"소스: {source_server}")
                    print(f"타겟: {target_server}")
                    print(f"테이블: {target_table}")
                    print(f"작업자 수: {num_workers}")
                    
                    start_time = time.time()
                    result = self.db_connector.parallel_migrate(
                        source_server, query, target_server, target_table, num_workers
                    )
                    end_time = time.time()
                    
                else:
                    print("❌ 잘못된 선택입니다.")
                    return
                
                # 결과 출력
                self._print_migration_result(result, end_time - start_time)
                
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
    
    def migrate_to_cloud_pgsql(self):
        """FS1에서 클라우드 PostgreSQL로 마이그레이션"""
        print("\n☁️ FS1 → 클라우드 PostgreSQL 마이그레이션")
        print("-" * 50)
        
        try:
            # 소스 서버 (FS1)
            source_server = 'FS1'
            
            # 타겟 서버 (클라우드 PostgreSQL)
            target_server = 'cloud_pgsql'
            
            # 쿼리 입력
            print("\n📝 소스 데이터 쿼리를 입력하세요:")
            query = self._get_multiline_input()
            
            if not query:
                print("❌ 쿼리가 입력되지 않았습니다.")
                return
            
            # 타겟 테이블명 입력
            target_table = input("\n📋 타겟 테이블명을 입력하세요: ").strip()
            if not target_table:
                print("❌ 테이블명이 입력되지 않았습니다.")
                return
            
            print(f"\n☁️ 클라우드 마이그레이션 시작...")
            print(f"소스: {source_server}")
            print(f"타겟: {target_server}")
            print(f"테이블: {target_table}")
            
            # 클라우드는 안정성을 위해 스트리밍 사용
            chunk_size = 5000  # 클라우드는 작은 청크 사용
            start_time = time.time()
            result = self.db_connector.stream_data(
                source_server, query, target_server, target_table, chunk_size
            )
            end_time = time.time()
            
            # 결과 출력
            self._print_migration_result(result, end_time - start_time)
            
        except Exception as e:
            print(f"❌ 클라우드 마이그레이션 실패: {e}")
    
    def execute_query(self):
        """쿼리 실행"""
        print("\n🔍 쿼리 실행")
        print("-" * 20)
        
        try:
            # 서버 선택
            server = self._select_server("쿼리를 실행할")
            if not server:
                return
            
            # 쿼리 입력
            print("\n📝 실행할 쿼리를 입력하세요:")
            query = self._get_multiline_input()
            
            if not query:
                print("❌ 쿼리가 입력되지 않았습니다.")
                return
            
            # 결과 형식 선택
            print("\n📊 결과 형식을 선택하세요:")
            print("1. 컬럼명과 함께 표시")
            print("2. 단순 결과만 표시")
            
            try:
                choice = int(input("선택 (1-2): "))
                if choice == 1:
                    result = self.db_connector.execute_query_with_columns(server, query)
                    self._print_query_result_with_columns(result)
                elif choice == 2:
                    result = self.db_connector.execute_query(server, query)
                    self._print_query_result(result)
                else:
                    print("❌ 잘못된 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 쿼리 실행 실패: {e}")
    
    def batch_migration(self):
        """배치 마이그레이션"""
        print("\n📦 배치 마이그레이션")
        print("-" * 30)
        
        try:
            # 마이그레이션 작업 목록
            migrations = [
                {
                    'name': '종목마스터',
                    'query': 'SELECT * FROM fds_팩셋."인포맥스종목마스터"',
                    'target_table': '종목마스터_배치'
                },
                {
                    'name': '거래소마스터',
                    'query': 'SELECT * FROM fds_팩셋."인포맥스거래소마스터"',
                    'target_table': '거래소마스터_배치'
                }
            ]
            
            print("배치 마이그레이션 작업:")
            for i, migration in enumerate(migrations, 1):
                print(f"{i}. {migration['name']} → {migration['target_table']}")
            
            # 실행할 작업 선택
            try:
                choice = int(input("\n실행할 작업을 선택하세요 (1-2): "))
                if 1 <= choice <= len(migrations):
                    migration = migrations[choice - 1]
                    
                    print(f"\n🚀 {migration['name']} 마이그레이션 시작...")
                    
                    start_time = time.time()
                    result = db_connection_test.quick_migrate(
                        source_server='FS1',
                        query=migration['query'],
                        target_server='local_pgsql',
                        target_table=migration['target_table'],
                        chunk_size=5000
                    )
                    end_time = time.time()
                    
                    self._print_migration_result(result, end_time - start_time)
                else:
                    print("❌ 잘못된 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 배치 마이그레이션 실패: {e}")
    
    def optimize_table(self):
        """테이블 최적화"""
        print("\n🔧 테이블 최적화")
        print("-" * 20)
        
        try:
            # 서버 선택
            server = self._select_server("최적화할 테이블이 있는")
            if not server:
                return
            
            # 테이블명 입력
            table_name = input("\n📋 테이블명을 입력하세요: ").strip()
            if not table_name:
                print("❌ 테이블명이 입력되지 않았습니다.")
                return
            
            print(f"\n🔧 테이블 최적화 중...")
            print(f"서버: {server}")
            print(f"테이블: {table_name}")
            
            success = self.db_connector.optimize_table(server, table_name)
            
            if success:
                print("✅ 테이블 최적화 완료!")
            else:
                print("❌ 테이블 최적화 실패")
                
        except Exception as e:
            print(f"❌ 테이블 최적화 실패: {e}")
    
    def manage_config(self):
        """설정 파일 관리"""
        print("\n⚙️ 설정 파일 관리")
        print("-" * 25)
        
        if not os.path.exists(self.config_file):
            print(f"❌ 설정 파일이 없습니다: {self.config_file}")
            print("템플릿 파일을 복사하여 설정 파일을 생성하세요.")
            print("cp db_connection_test/db_servers.template.ini db_connection_test/db_servers.ini")
            return
        
        print(f"📁 현재 설정 파일: {self.config_file}")
        
        # 설정 파일 내용 표시
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n📄 설정 파일 내용:")
                print("-" * 30)
                print(content)
        except Exception as e:
            print(f"❌ 설정 파일 읽기 실패: {e}")
    
    def _select_server(self, description: str) -> Optional[str]:
        """서버 선택"""
        servers = self.db_connector.get_server_list()
        
        if not servers:
            print(f"❌ 설정된 서버가 없습니다.")
            return None
        
        print(f"\n📋 {description} 서버를 선택하세요:")
        for i, server in enumerate(servers, 1):
            print(f"{i}. {server}")
        
        try:
            choice = int(input(f"\n선택 (1-{len(servers)}): "))
            if 1 <= choice <= len(servers):
                return servers[choice - 1]
            else:
                print("❌ 잘못된 선택입니다.")
                return None
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return None
    
    def _get_multiline_input(self) -> str:
        """여러 줄 입력 받기"""
        print("여러 줄 입력을 지원합니다. 입력 완료 후 빈 줄에서 Enter를 누르세요.")
        print("입력 시작:")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        return "\n".join(lines)
    
    def _get_chunk_size(self) -> int:
        """청크 크기 입력 받기"""
        while True:
            try:
                chunk_size = input("\n📦 청크 크기를 입력하세요 (기본값: 10000): ").strip()
                if not chunk_size:
                    return 10000
                
                chunk_size = int(chunk_size)
                if chunk_size > 0:
                    return chunk_size
                else:
                    print("❌ 0보다 큰 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _get_worker_count(self) -> int:
        """작업자 수 입력 받기"""
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        while True:
            try:
                workers = input(f"\n👥 작업자 수를 입력하세요 (권장: {cpu_count}, 기본값: 4): ").strip()
                if not workers:
                    return 4
                
                workers = int(workers)
                if 1 <= workers <= cpu_count * 2:
                    return workers
                else:
                    print(f"❌ 1에서 {cpu_count * 2} 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _print_migration_result(self, result: Dict[str, Any], duration: float):
        """마이그레이션 결과 출력"""
        print("\n" + "="*50)
        print("✅ 마이그레이션 완료!")
        print("="*50)
        print(f"📊 처리된 행 수: {result['total_rows']:,}")
        print(f"📦 처리된 크기: {result['total_size_mb']:.2f}MB")
        print(f"⏱️ 소요 시간: {duration:.2f}초")
        print(f"🚀 처리 속도: {result['rows_per_second']:.0f}행/초")
        print(f"💾 데이터 속도: {result['mb_per_second']:.2f}MB/초")
        
        if 'workers_used' in result:
            print(f"👥 사용된 작업자: {result['workers_used']}개")
    
    def _print_query_result(self, result: List[tuple]):
        """쿼리 결과 출력"""
        print(f"\n📊 쿼리 결과 ({len(result)}행):")
        print("-" * 40)
        
        for i, row in enumerate(result, 1):
            print(f"{i:3d}. {row}")
    
    def _print_query_result_with_columns(self, result: Dict[str, Any]):
        """컬럼명과 함께 쿼리 결과 출력"""
        print(f"\n📊 쿼리 결과 ({result['row_count']}행):")
        print("-" * 40)
        
        if result['columns']:
            print(f"컬럼: {result['columns']}")
            print("-" * 40)
        
        for i, row in enumerate(result['rows'], 1):
            print(f"{i:3d}. {row}")
    
    def run(self):
        """도구 실행"""
        while True:
            try:
                self.show_menu()
                choice = input("\n선택하세요 (0-7): ").strip()
                
                if choice == '0':
                    print("\n👋 프로그램을 종료합니다.")
                    break
                elif choice == '1':
                    self.test_connections()
                elif choice == '2':
                    self.migrate_to_local_pgsql()
                elif choice == '3':
                    self.migrate_to_cloud_pgsql()
                elif choice == '4':
                    self.execute_query()
                elif choice == '5':
                    self.optimize_table()
                elif choice == '6':
                    self.manage_config()
                elif choice == '7':
                    self.batch_migration()
                else:
                    print("❌ 잘못된 선택입니다. 0-7 사이의 숫자를 입력해주세요.")
                
                input("\nEnter를 누르면 계속...")
                
            except KeyboardInterrupt:
                print("\n\n👋 프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"\n❌ 오류가 발생했습니다: {e}")
                input("Enter를 누르면 계속...")
        
        self.db_connector.close_all()


def main():
    """메인 함수"""
    print("🚀 FS Master 데이터 마이그레이션 도구 시작")
    
    # 설정 파일 확인
    config_file = 'db_connection_test/db_servers.ini'
    if not os.path.exists(config_file):
        print(f"⚠️ 설정 파일이 없습니다: {config_file}")
        print("템플릿 파일을 복사하여 설정 파일을 생성하세요.")
        print("cp db_connection_test/db_servers.template.ini db_connection_test/db_servers.ini")
        return
    
    # 도구 실행
    tool = FSMigrationTool(config_file)
    tool.run()


if __name__ == "__main__":
    main() 