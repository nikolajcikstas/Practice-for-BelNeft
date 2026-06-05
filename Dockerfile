# Stage 1: build React frontend
FROM node:20-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: runtime (Python + nginx + supervisor)
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY --from=frontend /frontend/dist /var/www/html

COPY hf/nginx.conf /etc/nginx/sites-available/default
COPY hf/supervisord_simple.conf /etc/supervisor/conf.d/app.conf
COPY hf/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 7860

CMD ["/start.sh"]
