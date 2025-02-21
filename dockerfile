FROM python:3.11-alpine

WORKDIR /app/server

COPY requirements.txt /app/

RUN apk add --no-cache \
    build-base \
    gcc \
    g++ \
    musl-dev \
    python3-dev

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY server/ /app/server/

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["flask", "run"]
