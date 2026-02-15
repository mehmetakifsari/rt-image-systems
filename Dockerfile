# =============================================
# Renault Trucks Garanti Kayıt Sistemi
# Multi-stage Dockerfile for Coolify Deployment
# =============================================

# Stage 1: Build Frontend
FROM node:20-bullseye-slim as build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/yarn.lock* ./

# Install dependencies (more resilient)
RUN yarn install --network-timeout 300000 --frozen-lockfile 2>/dev/null || \
    yarn install --network-timeout 300000

# Copy frontend source
COPY frontend/ ./

# Build arguments for environment
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_GA_MEASUREMENT_ID
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV REACT_APP_GA_MEASUREMENT_ID=${REACT_APP_GA_MEASUREMENT_ID}

# Build the frontend
RUN yarn build

# Stage 2: Production Image
FROM python:3.11-slim-bullseye as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
# - build deps: grpcio/cryptography/numpy/pandas gibi paketler source'a düşerse derlemek için
# - nginx/supervisor: runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    ca-certificates \
    # build deps
    build-essential gcc g++ python3-dev \
    libffi-dev libssl-dev \
    libjpeg-dev zlib1g-dev \
    # bazı durumlarda cryptography source build için gerekebilir
    rustc cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/requirements.txt

# Upgrade pip tooling + install deps (verbose build log for easier debug)
RUN python -m pip install -U pip setuptools wheel \
    && pip install -r backend/requirements.txt -v

# (Opsiyonel) build deps'i kaldırıp image'i küçültmek istersen aç:
# RUN apt-get purge -y --auto-remove \
#     build-essential gcc g++ python3-dev \
#     libffi-dev libssl-dev libjpeg-dev zlib1g-dev \
#     rustc cargo \
#     && rm -rf /var/lib/apt/lists/*

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from build stage
COPY --from=build /app/frontend/build ./frontend/build

# Create uploads directory
RUN mkdir -p /app/backend/uploads/standard \
    /app/backend/uploads/roadassist \
    /app/backend/uploads/damaged \
    /app/backend/uploads/pdi

# Nginx configuration
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Supervisor configuration
# Not: Eğer bu dosya "program config" ise conf.d içine,
# eğer "main supervisord.conf" ise /etc/supervisor/supervisord.conf içine koymalısın.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/ || exit 1

# Start supervisor
# Debian/Ubuntu'da genelde ana config /etc/supervisor/supervisord.conf olur.
# Sen conf.d içine koyduğun için default ana config ile başlatmak daha sağlıklı:
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
