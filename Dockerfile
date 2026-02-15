# =============================================
# Renault Trucks Garanti Kayıt Sistemi
# Multi-stage Dockerfile for Coolify Deployment
# =============================================

# Stage 1: Build Frontend
FROM node:20-bullseye-slim as build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile || yarn install

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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

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
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/ || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
