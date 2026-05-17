FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml

# Install dependencies only. Source is mounted at runtime via Compose so that
# editing files on the host hot-reloads inside the container.
RUN pip install --upgrade pip && \
    pip install \
        "fastapi>=0.110,<1.0" \
        "uvicorn[standard]>=0.27,<1.0" \
        "sqlalchemy>=2.0,<3.0" \
        "alembic>=1.13,<2.0" \
        "psycopg[binary]>=3.1,<4.0" \
        "pydantic>=2.6,<3.0" \
        "pydantic-settings>=2.2,<3.0" \
        "python-dotenv>=1.0,<2.0" \
        "httpx>=0.27,<1.0" \
        "structlog>=24.1,<25.0" \
        "pytest>=8.0,<9.0" \
        "pytest-asyncio>=0.23,<1.0" \
        "respx>=0.21,<1.0" \
        "ruff>=0.4,<1.0" \
        "black>=24.0,<25.0"

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
