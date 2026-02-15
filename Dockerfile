# Stage 2: Production Image
FROM python:3.11-slim-bullseye as production

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

# Frontend
COPY --from=build /app/frontend/build ./frontend/build

# Upload klasörleri
RUN mkdir -p /app/backend/uploads/standard \
    /app/backend/uploads/roadassist \
    /app/backend/uploads/damaged \
    /app/backend/uploads/pdi

# Nginx config
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD bash -c "uvicorn backend.server:app --host 0.0.0.0 --port 8001 & nginx -g 'daemon off;'"
