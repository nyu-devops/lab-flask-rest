FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY config.py ./
COPY service ./service

# Expose any ports the app is expecting in the environment
ENV PORT 5000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--log-level=info", "service:app"]
