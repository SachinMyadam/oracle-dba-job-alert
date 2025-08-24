import requests
import time
import random
import logging
import sqlite3
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
import json
import schedule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OracleDBAJobScraper:
    def __init__(self, config_file='config_example.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.db_path = self.config.get('database_path', 'oracle_jobs.db')
        self.user_agent = self.config.get('user_agent', 'Mozilla/5.0')
        self.headers = {'User-Agent': self.user_agent}
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                company_name TEXT,
                job_title TEXT,
                location TEXT,
                experience_required TEXT,
                salary_range TEXT,
                job_description TEXT,
                application_url TEXT,
                posting_date TEXT,
                application_deadline TEXT,
                scraped_date TEXT,
                source_portal TEXT,
                hash TEXT
            )
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_hash ON jobs(hash)')
        conn.commit()
        conn.close()
        logging.info('Database initialized')

    def request_with_rate_limit(self, url):
        delay = random.uniform(self.config.get('request_delay', {}).get('min', 1),
                               self.config.get('request_delay', {}).get('max', 3))
        time.sleep(delay)
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.config.get('timeout', 10))
            if resp.status_code == 200:
                return resp
            logging.warning(f'Non-200 response ({resp.status_code}) for {url}')
        except Exception as e:
            logging.error(f'Request error for {url}: {e}')
        return None

    def job_hash(self, company, title, location):
        s = f"{company}|{title}|{location}"
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def save_job(self, job):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO jobs (job_id, company_name, job_title, location, experience_required,
                                  salary_range, job_description, application_url, posting_date,
                                  application_deadline, scraped_date, source_portal, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['job_id'], job['company_name'], job['job_title'], job['location'],
                job.get('experience_required', ''), job.get('salary_range', ''), job.get('job_description', ''),
                job.get('application_url', ''), job.get('posting_date', ''), job.get('application_deadline', ''),
                job.get('scraped_date', ''), job.get('source_portal', ''), job.get('hash', '')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            logging.info(f'Duplicate job skipped: {job["job_id"]}')
            return False
        finally:
            conn.close()

    def scrape_naukri(self):
        print("Starting scrape_naukri()...")

        search_url = self.config['job_portals'].get('naukri')
        if not search_url:
            print("No Naukri search URL in config")
            return []

        resp = self.request_with_rate_limit(search_url)
        print("Naukri HTTP GET request done")
        if not resp:
            print("Naukri HTTP request failed or timed out")
            return []
        print("Naukri HTTP request succeeded")

        print(resp.text[:1000])  # Print first 1000 chars of HTML for debugging

        soup = BeautifulSoup(resp.text, 'lxml')
        jobs = []
        # Updated selector to match the current Naukri page structure
        cards = soup.select('div.srp-jobtuple-wrapper, div.cust-job-tuple')
        print(f"Found {len(cards)} job cards on Naukri")

        for c in cards:
            try:
                title_el = c.select_one('a.title')
                comp_el = c.select_one('a.comp-name')
                loc_el = c.select_one('span.locWdth')
                exp_el = c.select_one('span.expwdth')
                desc_el = c.select_one('span.job-description')

                title = title_el.get_text(strip=True) if title_el else ''
                company = comp_el.get_text(strip=True) if comp_el else ''
                location = loc_el.get_text(strip=True) if loc_el else ''
                experience = exp_el.get_text(strip=True) if exp_el else ''
                description = desc_el.get_text(strip=True) if desc_el else ''
                url = title_el['href'] if title_el and title_el.has_attr('href') else ''

                if not title or not company:
                    continue
                if 'oracle' not in title.lower() or 'dba' not in title.lower():
                    continue

                jhash = self.job_hash(company, title, location)
                job = {
                    'job_id': f'naukri_{jhash[:10]}',
                    'company_name': company,
                    'job_title': title,
                    'location': location,
                    'experience_required': experience,
                    'job_description': description,
                    'application_url': url,
                    'scraped_date': datetime.now().isoformat(),
                    'source_portal': 'Naukri',
                    'hash': jhash
                }
                jobs.append(job)
            except Exception as e:
                logging.error(f'Naukri parse error: {e}')
                continue

        print(f'scrape_naukri(): returning {len(jobs)} jobs')
        return jobs

    def scrape_indeed(self):
        print("Starting scrape_indeed()...")

        search_url = self.config['job_portals'].get('indeed')
        if not search_url:
            print("No Indeed search URL in config")
            return []

        resp = self.request_with_rate_limit(search_url)
        print("Indeed HTTP GET request done")
        if not resp:
            print("Indeed HTTP request failed or timed out")
            return []
        print("Indeed HTTP request succeeded")

        soup = BeautifulSoup(resp.text, 'lxml')
        jobs = []
        cards = soup.select('div.job_seen_beacon, td.resultContent')
        print(f"Found {len(cards)} job cards on Indeed")

        for c in cards:
            try:
                title_el = c.select_one('h2.jobTitle a')
                comp_el = c.select_one('span.companyName')
                loc_el = c.select_one('div.companyLocation')
                desc_el = c.select_one('div.job-snippet')

                title = title_el.get_text(strip=True) if title_el else ''
                company = comp_el.get_text(strip=True) if comp_el else ''
                location = loc_el.get_text(strip=True) if loc_el else ''
                description = desc_el.get_text(" ", strip=True) if desc_el else ''
                url = title_el['href'] if title_el and title_el.has_attr('href') else ''

                if not title or not company:
                    continue
                if 'oracle' not in title.lower() or 'dba' not in title.lower():
                    continue

                jhash = self.job_hash(company, title, location)
                job = {
                    'job_id': f'indeed_{jhash[:10]}',
                    'company_name': company,
                    'job_title': title,
                    'location': location,
                    'experience_required': '',
                    'job_description': description,
                    'application_url': url,
                    'scraped_date': datetime.now().isoformat(),
                    'source_portal': 'Indeed',
                    'hash': jhash
                }
                jobs.append(job)
            except Exception as e:
                logging.error(f'Indeed parse error: {e}')
                continue

        print(f'scrape_indeed(): returning {len(jobs)} jobs')
        return jobs

    def run_once(self):
        logging.info("Running one scraping cycle...")
        total_saved = 0
        for scraper_method in [self.scrape_naukri, self.scrape_indeed]:
            jobs = scraper_method()
            for job in jobs:
                if self.save_job(job):
                    total_saved += 1
        logging.info(f'Total new jobs saved: {total_saved}')

    def schedule_daily(self):
        schedule_time = self.config.get('schedule_time', '09:00')
        schedule.every().day.at(schedule_time).do(self.run_once)
        logging.info(f'Scheduler set. Running daily at {schedule_time}')
        while True:
            schedule.run_pending()
            time.sleep(30)

def main():
    scraper = OracleDBAJobScraper()
    scraper.run_once()

if __name__ == "__main__":
    main()
