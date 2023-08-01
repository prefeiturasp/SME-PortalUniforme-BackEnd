FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project and install dependencies
WORKDIR /code
COPY . /code/
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libpq-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0  && \
    pip install psycopg2-binary && \
    pip --no-cache-dir install --upgrade pip && \
    pip --no-cache-dir install --requirement requirements/production.txt && \
    apt-get remove -y gcc g++ && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8001
