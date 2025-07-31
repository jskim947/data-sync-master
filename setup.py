"""
FS Master Web Application Setup

웹 애플리케이션 초기 설정 스크립트
"""

import os
import sys
import subprocess
import configparser
from pathlib import Path

def run_command(command, description):
    """명령어 실행"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패: {e}")
        print(f"오류 출력: {e.stderr}")
        return False

def create_postgresql_database():
    """PostgreSQL 데이터베이스 생성"""
    print("\n🗄️ PostgreSQL 데이터베이스 설정")
    print("=" * 50)
    
    # PostgreSQL 연결 정보 입력
    host = input("PostgreSQL 호스트 (기본값: localhost): ").strip() or "localhost"
    port = input("PostgreSQL 포트 (기본값: 5432): ").strip() or "5432"
    user = input("PostgreSQL 사용자 (기본값: postgres): ").strip() or "postgres"
    password = input("PostgreSQL 비밀번호: ").strip()
    
    if not password:
        print("❌ 비밀번호는 필수입니다.")
        return False
    
    # 데이터베이스 생성 명령어
    create_db_command = f'psql -h {host} -p {port} -U {user} -c "CREATE DATABASE fs_master_web;"'
    
    # 환경변수 설정
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    print(f"🔄 데이터베이스 'fs_master_web' 생성 중...")
    try:
        result = subprocess.run(create_db_command, shell=True, env=env, capture_output=True, text=True)
        if result.returncode == 0 or "already exists" in result.stderr:
            print("✅ 데이터베이스 생성 완료 (또는 이미 존재)")
        else:
            print(f"⚠️ 데이터베이스 생성 중 경고: {result.stderr}")
    except Exception as e:
        print(f"❌ 데이터베이스 생성 실패: {e}")
        return False
    
    # app.py의 데이터베이스 URI 업데이트
    update_database_uri(host, port, user, password)
    
    return True

def update_database_uri(host, port, user, password):
    """app.py의 데이터베이스 URI 업데이트"""
    app_py_path = Path("app.py")
    if app_py_path.exists():
        content = app_py_path.read_text(encoding='utf-8')
        
        # 기존 URI 라인 찾기 및 교체
        old_uri_line = 'app.config[\'SQLALCHEMY_DATABASE_URI\'] = \'postgresql://postgres:your_password@localhost/fs_master_web\''
        new_uri_line = f"app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}:{port}/fs_master_web'"
        
        if old_uri_line in content:
            content = content.replace(old_uri_line, new_uri_line)
            app_py_path.write_text(content, encoding='utf-8')
            print("✅ app.py 데이터베이스 URI 업데이트 완료")
        else:
            print("⚠️ app.py에서 데이터베이스 URI를 찾을 수 없습니다. 수동으로 확인해주세요.")

def install_dependencies():
    """의존성 설치"""
    print("\n📦 의존성 설치")
    print("=" * 50)
    
    # db_connection_test 패키지 설치
    if not run_command("cd db_connection_test && pip install -e .", "db_connection_test 패키지 설치"):
        return False
    
    # 웹 애플리케이션 의존성 설치
    if not run_command("pip install -r requirements.txt", "웹 애플리케이션 의존성 설치"):
        return False
    
    return True

def create_initial_config():
    """초기 설정 파일 생성"""
    print("\n⚙️ 초기 설정 파일 생성")
    print("=" * 50)
    
    # db_servers.ini 생성
    config_path = Path("db_connection_test/db_servers.ini")
    if not config_path.exists():
        template_path = Path("db_connection_test/db_servers.template.ini")
        if template_path.exists():
            config_path.write_text(template_path.read_text(encoding='utf-8'), encoding='utf-8')
            print("✅ db_servers.ini 파일 생성 완료")
        else:
            print("❌ db_servers.template.ini 파일을 찾을 수 없습니다.")
            return False
    else:
        print("ℹ️ db_servers.ini 파일이 이미 존재합니다.")
    
    return True

def setup_database_tables():
    """데이터베이스 테이블 생성"""
    print("\n🗃️ 데이터베이스 테이블 생성")
    print("=" * 50)
    
    # Flask 애플리케이션 실행하여 테이블 생성
    if not run_command("python app.py --setup-only", "데이터베이스 테이블 생성"):
        print("⚠️ 수동으로 테이블을 생성해야 할 수 있습니다.")
        print("   python app.py를 실행하여 애플리케이션을 시작하세요.")
        return False
    
    return True

def main():
    """메인 설정 함수"""
    print("🚀 FS Master Web Application Setup")
    print("=" * 60)
    print("이 스크립트는 FS Master 웹 애플리케이션의 초기 설정을 수행합니다.")
    print()
    
    # 1. 의존성 설치
    if not install_dependencies():
        print("❌ 의존성 설치에 실패했습니다.")
        return False
    
    # 2. PostgreSQL 데이터베이스 설정
    if not create_postgresql_database():
        print("❌ PostgreSQL 데이터베이스 설정에 실패했습니다.")
        return False
    
    # 3. 초기 설정 파일 생성
    if not create_initial_config():
        print("❌ 초기 설정 파일 생성에 실패했습니다.")
        return False
    
    # 4. 데이터베이스 테이블 생성
    if not setup_database_tables():
        print("⚠️ 데이터베이스 테이블 생성에 문제가 있을 수 있습니다.")
    
    print("\n🎉 설정 완료!")
    print("=" * 60)
    print("다음 단계:")
    print("1. db_connection_test/db_servers.ini 파일을 편집하여 실제 서버 정보를 입력하세요.")
    print("2. python app.py를 실행하여 웹 애플리케이션을 시작하세요.")
    print("3. 브라우저에서 http://localhost:5000으로 접속하세요.")
    print()
    print("추가 설정:")
    print("- 서버 관리에서 데이터베이스 서버를 추가하세요.")
    print("- 배치 작업을 생성하고 스케줄을 설정하세요.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1) 