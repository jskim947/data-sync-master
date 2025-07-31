"""
FS Master Migration Example

db_connection_test를 import하여 사용하는 마이그레이션 예시
"""

import db_connection_test
import time

def main():
    """메인 함수"""
    print("🚀 FS Master 마이그레이션 예시")
    print("=" * 50)

    try:
        # 1. 기본 커넥터 사용
        print("\n1️⃣ 기본 커넥터 사용")
        with db_connection_test.SimpleDatabaseConnector('db_connection_test/db_servers.ini') as db:
            # 서버 목록 확인
            servers = db.get_server_list()
            print(f"사용 가능한 서버: {servers}")

            if 'FS1' in servers:
                # 쿼리 실행
                result = db.execute_query_with_columns(
                    'FS1',
                    'SELECT COUNT(*) as total FROM fds_팩셋."인포맥스종목마스터"'
                )
                print(f"총 종목 수: {result['rows'][0][0]:,}")

        # 2. FS1 → 로컬 PostgreSQL 마이그레이션
        print("\n2️⃣ FS1 → 로컬 PostgreSQL 마이그레이션")
        if 'FS1' in servers and 'local_pgsql' in servers:
            # 빠른 마이그레이션
            result = db_connection_test.quick_migrate(
                source_server='FS1',
                query='SELECT * FROM fds_팩셋."인포맥스종목마스터" LIMIT 100',
                target_server='local_pgsql',
                target_table='종목마스터_로컬',
                chunk_size=50
            )
            print(f"로컬 마이그레이션 완료: {result['total_rows']:,}행")
            print(f"소요 시간: {result['duration_seconds']:.2f}초")

        # 3. FS1 → 클라우드 PostgreSQL 마이그레이션
        print("\n3️⃣ FS1 → 클라우드 PostgreSQL 마이그레이션")
        if 'FS1' in servers and 'cloud_pgsql' in servers:
            result = db_connection_test.quick_migrate(
                source_server='FS1',
                query='SELECT * FROM fds_팩셋."인포맥스종목마스터" LIMIT 50',
                target_server='cloud_pgsql',
                target_table='종목마스터_클라우드',
                chunk_size=25
            )
            print(f"클라우드 마이그레이션 완료: {result['total_rows']:,}행")
            print(f"소요 시간: {result['duration_seconds']:.2f}초")

        # 4. 병렬 마이그레이션
        print("\n4️⃣ 병렬 마이그레이션")
        if 'FS1' in servers and 'local_pgsql' in servers:
            result = db_connection_test.parallel_migrate(
                source_server='FS1',
                query='SELECT * FROM fds_팩셋."인포맥스종목마스터" LIMIT 200',
                target_server='local_pgsql',
                target_table='종목마스터_병렬',
                num_workers=2
            )
            print(f"병렬 마이그레이션 완료: {result['total_rows']:,}행")
            print(f"사용된 작업자: {result['workers_used']}개")

        # 5. 테이블 최적화
        print("\n5️⃣ 테이블 최적화")
        if 'local_pgsql' in servers:
            with db_connection_test.SimpleDatabaseConnector('db_connection_test/db_servers.ini') as db:
                success = db.optimize_table('local_pgsql', '종목마스터_로컬')
                if success:
                    print("✅ 테이블 최적화 완료!")
                else:
                    print("❌ 테이블 최적화 실패")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("설정 파일(db_connection_test/db_servers.ini)을 확인해주세요.")

if __name__ == "__main__":
    main() 