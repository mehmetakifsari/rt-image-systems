# =============================================
# Renault Trucks Garanti Kayıt Sistemi
# Multi-stage Dockerfile for Coolify Deployment
# (Supervisor yok - nginx + uvicorn)
# =============================================

# Stage 1: Build Frontend
FROM node:20-bullseye-slim AS build

WORKDIR /app/frontend

COPY frontend/package.json frontend/yarn.lock* ./

RUN yarn install --network-timeout 300000 --frozen-lockfile 2>/dev/null || \
    yarn install --network-timeout 300000

COPY frontend/ ./

ARG REACT_APP_BACKEND_URL
ARG REACT_APP_GA_MEASUREMENT_ID
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV REACT_APP_GA_MEASUREMENT_ID=${REACT_APP_GA_MEASUREMENT_ID}

RUN yarn build


# Stage 2: Production
FROM python:3.11-slim-bullseye AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    ca-certificates \
    build-essential gcc g++ python3-dev \
    libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r backend/requirements.txt

# Backend source
COPY backend/ ./backend/

# Frontend build
COPY --from=build /app/frontend/build /app/frontend/build

# Upload klasörleri
RUN mkdir -p /app/backend/uploads/standard \
    /app/backend/uploads/roadassist \
    /app/backend/uploads/damaged \
    /app/backend/uploads/pdi

# Nginx config
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Uvicorn + Nginx (aynı container)
CMD bash -c "uvicorn server:app --host 0.0.0.0 --port 8001 --app-dir /app/backend & nginx -g 'daemon off;'"
