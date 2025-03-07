# ./streaming_server/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN pip install Flask

COPY streaming_server.py .

CMD ["python", "streaming_server.py"]
