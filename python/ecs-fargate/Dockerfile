FROM --platform=linux/amd64 python:3.12

RUN pip install flask uwsgi ddtrace

EXPOSE 80

COPY webapp.py .

CMD ["ddtrace-run", "uwsgi", "--http", ":80", "--wsgi-file", "webapp.py", "--callable", "app"]
