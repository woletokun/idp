import os
import psycopg2
import redis
import requests
from bs4 import BeautifulSoup

# Real Postgres connection info from infra manifests
POSTGRES_HOST = "postgres.infra.svc.cluster.local"
POSTGRES_DB = "jobs"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")  # from Secret

REDIS_HOST = "redis.infra.svc.cluster.local"
REDIS_PORT = 6379

def connect_postgres():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def connect_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def scrape_jobs(keyword="DevOps"):
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job_card in soup.select(".base-card"):
        title = job_card.select_one(".base-search-card__title").get_text(strip=True)
        company = job_card.select_one(".base-search-card__subtitle").get_text(strip=True)
        location = job_card.select_one(".job-search-card__location").get_text(strip=True)
        jobs.append((title, company, location))
    return jobs

def save_jobs(jobs):
    conn = connect_postgres()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS linkedin_jobs (
            id SERIAL PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            CONSTRAINT unique_job_entry UNIQUE (title, company, location)
        )
    """)
    for title, company, location in jobs:
        cur.execute("""
            INSERT INTO linkedin_jobs (title, company, location) 
            VALUES (%s, %s, %s)
            ON CONFLICT (title, company, location) DO NOTHING
        """, (title, company, location))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    jobs = scrape_jobs("DevOps Engineer")
    save_jobs(jobs)
    print(f"Saved {len(jobs)} jobs to Postgres")
