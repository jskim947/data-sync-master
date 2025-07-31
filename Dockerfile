FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# AdoptOpenJDK 11 설치 (더 간단한 방법)
RUN wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | apt-key add - \
    && echo "deb https://packages.adoptium.net/artifactory/deb bookworm main" | tee /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y temurin-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# JAVA_HOME 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/temurin-11-jdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Java 버전 확인 및 환경 정보 출력
RUN java -version && echo "JAVA_HOME: $JAVA_HOME" && echo "PATH: $PATH"

# Python 의존성 파일 복사 및 설치 (자주 변경되지 않음)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir tzdata

# 애플리케이션 파일 복사
COPY app.py .
COPY templates/ templates/
COPY db_connection_test/ db_connection_test/

# 로그 디렉토리 생성
RUN mkdir -p logs

# 포트 노출
EXPOSE 5000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 애플리케이션 실행
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"] 