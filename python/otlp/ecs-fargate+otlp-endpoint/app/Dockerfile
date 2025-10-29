FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt && opentelemetry-bootstrap -a install

COPY app.py .

EXPOSE 8080

CMD ["opentelemetry-instrument", "gunicorn", "--bind", "0.0.0.0:8080", "--log-level", "debug", "app:app"]
