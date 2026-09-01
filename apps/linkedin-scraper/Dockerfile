FROM python:3.11-slim

WORKDIR /app
COPY scraper.py /app

RUN pip install requests beautifulsoup4 psycopg2-binary redis

CMD ["python", "scraper.py"]
