FROM public.ecr.aws/lambda/python:latest

COPY handler.py .
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

CMD ["handler.handle"]
