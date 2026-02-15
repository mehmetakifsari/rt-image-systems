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

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    ca-certificates \
    # build deps (pip bazı paketlerde kaynak derlemeye düşerse)
    build-essential gcc g++ python3-dev \
    libffi-dev libssl-dev \
    libjpeg-dev zlib1g-dev \
    rustc cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/requirements.txt

RUN python -m pip install -U pip setuptools wheel \
    && pip install -r backend/requirements.txt -v

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend
COPY --from=build /app/frontend/build ./frontend/build

# Uploads directory
RUN mkdir -p /app/backend/uploads/standard \
    /app/backend/uploads/roadassist \
    /app/backend/uploads/damaged \
    /app/backend/uploads/pdi

# Nginx config
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# -----------------------------
# Supervisor: "ana config" dosyasını biz yazıyoruz.
# conf.d altına da app programlarını ayrı dosya olarak koyuyoruz.
# Böylece "supervisord.conf" isim çakışmaları / yanlış kopyalama sorunları bitiyor.
# -----------------------------

# Ana supervisord config
RUN printf '%s\n' \
"[supervisord]" \
"nodaemon=true" \
"logfile=/var/log/supervisor/supervisord.log" \
"pidfile=/var/run/supervisord.pid" \
"childlogdir=/var/log/supervisor" \
"" \
"[unix_http_server]" \
"file=/var/run/supervisor.sock" \
"" \
"[rpcinterface:supervisor]" \
"supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" \
"" \
"[supervisorctl]" \
"serverurl=unix:///var/run/supervisor.sock" \
"" \
"[include]" \
"files = /etc/supervisor/conf.d/*.conf" \
> /etc/supervisor/supervisord.conf

# Senin gönderdiğin supervisord.conf içeriği aslında "program config".
# İsim çakışmasını önlemek için app.conf diye kopyalıyoruz:
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/ || exit 1

# Start supervisor (ana config ile)
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
