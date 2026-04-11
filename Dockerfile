FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY run.py .
COPY start.sh .

RUN useradd -m -u 1000 fortrx && \
    chown -R fortrx:fortrx /app

USER fortrx

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["./start.sh"]