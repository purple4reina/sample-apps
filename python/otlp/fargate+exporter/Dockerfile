FROM --platform=linux/amd64 python:3.12

RUN pip install flask gunicorn ddtrace

EXPOSE 80

COPY webapp.py .

CMD ["ddtrace-run", "gunicorn", "-b", "127.0.0.1:80", "--log-level", "debug", "webapp:app"]
