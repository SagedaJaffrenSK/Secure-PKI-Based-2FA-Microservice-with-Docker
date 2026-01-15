FROM python:3.11-slim

ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install packages explicitly to the system python
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir uvicorn gunicorn fastapi cryptography pyotp python-multipart

# Copy the rest of the application
COPY . .

# Fix Cron: Remove Windows line endings and ensure newline
RUN cp cron/2fa-cron /etc/cron.d/2fa-cron && \
    sed -i 's/\r$//' /etc/cron.d/2fa-cron && \
    echo "" >> /etc/cron.d/2fa-cron && \
    chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Use python3 -m uvicorn as the direct entrypoint
CMD ["sh", "-c", "cron && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]