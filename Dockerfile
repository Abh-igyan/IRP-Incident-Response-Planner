FROM node:20-alpine AS frontend-build
WORKDIR /src/frontend

COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

FROM python:3.10-slim AS backend-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY models/ /app/models/
COPY datasets/ /app/datasets/
COPY graphs/ /app/graphs/
COPY analytics/ /app/analytics/
COPY analytics_exports/ /app/analytics_exports/
COPY --from=frontend-build /src/frontend/dist /app/frontend/dist

WORKDIR /app/backend
EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
