FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV REPORTS_DIR=/reports
CMD ["python", "-m", "app.analytics_service"]
