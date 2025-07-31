#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""db_connection_test 모듈 테스트"""

import sys
import os

# db_connection_test import
from db_connection_test import get_server_config, execute_query

def test_connection(server_name):
    """연결 테스트"""
    try:
        conf = get_server_config(server_name)
        db_type = conf['type']
        
        # 간단한 테스트 쿼리
        if db_type == 'postgresql':
            test_query = "SELECT 1 as test"
        else:
            test_query = "SELECT 1 FROM DUAL"
        
        result, success, error = execute_query(server_name, test_query)
        
        if success:
            print(f"✅ {server_name} ({db_type}) 연결 성공")
            print(f"   테스트 결과: {result}")
            return True
        else:
            print(f"❌ {server_name} ({db_type}) 연결 실패")
            print(f"   오류: {error}")
            return False
            
    except Exception as e:
        print(f"❌ {server_name} 연결 테스트 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🔍 db_connection_test 모듈 테스트")
    print("=" * 50)
    
    # 테스트할 서버 목록
    test_servers = ['local_pgsql', 'm7', 'FS1']
    
    for server in test_servers:
        print(f"\n📡 {server} 서버 테스트 중...")
        test_connection(server)
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == '__main__':
    main() 