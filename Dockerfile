FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGROFIELD_DB_PATH=/data/agrofield.sqlite3

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 agrofield && mkdir -p /data && chown agrofield:agrofield /data
USER agrofield

EXPOSE 8000
# Hosts such as Render, Railway and Hugging Face inject PORT; default to 8000.
CMD ["sh", "-c", "uvicorn agrofield_agent.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
