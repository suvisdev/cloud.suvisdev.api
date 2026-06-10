# 1. Python이 설치된 기본 환경을 가져옵니다.
FROM python:3.14.5-slim

# 2. 도커 내부에서 작업할 폴더 위치를 지정합니다.
WORKDIR /suvisdev

# 3. 라이브러리 설치를 위해 패키지 파일을 먼저 복사합니다.
COPY requirements.txt .

# 4. 백엔드에 필요한 라이브러리들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 내 컴퓨터의 suvisdev 폴더 안 소스코드를 도커 컴퓨터로 전부 복사합니다.
COPY . .

# 6. 도커가 실행될 때 FastAPI를 8000포트로 실행합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
