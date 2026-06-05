# Stage 1: build React frontend
FROM node:20-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: runtime
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY --from=frontend /frontend/dist /var/www/html

COPY hf/nginx.conf /etc/nginx/conf.d/default.conf
COPY hf/supervisord_simple.conf /etc/supervisor/conf.d/app.conf
COPY hf/start.sh /start.sh
RUN chmod +x /start.sh

ENV PORT=7860
EXPOSE 7860

CMD ["/start.sh"]
