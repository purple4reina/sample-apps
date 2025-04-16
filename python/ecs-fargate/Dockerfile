FROM --platform=linux/amd64 python:3.12

RUN pip install flask uwsgi

EXPOSE 80

COPY webapp.py .

CMD ["uwsgi", "--http", ":80", "--wsgi-file", "webapp.py", "--callable", "app"]
