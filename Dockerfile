FROM python:3-slim
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 boto3[rds]

COPY main.py .
CMD python main.py