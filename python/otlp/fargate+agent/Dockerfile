FROM --platform=linux/amd64 python:3.12

RUN pip install gunicorn ddtrace

COPY webapp.py .

CMD ["ddtrace-run", "gunicorn", "-b", ":3000", "--log-level", "debug", "webapp:app"]
