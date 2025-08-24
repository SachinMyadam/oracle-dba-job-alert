import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import time
import smtplib
from email.mime.text import MIMEText
import os

DB_NAME = "jobs.db"
SENDER_EMAIL = "nanisachin45@gmail.com"  # Replace with your email
SENDER_PASSWORD = "mtcu tkjf sxcb fqqc"  # Replace with your app password
RECIPIENT_EMAIL = "nanisachin45@gmail.com"  # Replace with your email

def scrape_indeed_jobs():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    url = "https://in.indeed.com/jobs?q=oracle+dba&l=India"
    driver.get(url)
    print("Browser loaded URL.")

    # Scroll and wait for job cards to load
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mosaic-provider-jobcards"))
    )
    print("Job cards container loaded.")

    jobs = []
    job_cards = driver.find_elements(By.CSS_SELECTOR, '#mosaic-provider-jobcards [data-testid="slider_container"]')

    for card in job_cards:
        try:
            title_el = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
            title = title_el.text
            url = title_el.get_attribute('href')
        except:
            title, url = "", ""

        try:
            company_el = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]')
            company = company_el.text
        except:
            company = ""

        try:
            location_el = card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]')
            location = location_el.text
        except:
            location = ""

        jobs.append({
            "title": title,
            "url": url,
            "company": company,
            "location": location
        })

    driver.quit()
    return jobs

def save_jobs_to_sqlite(jobs, db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS oracle_dba_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            company TEXT,
            location TEXT
        )
    ''')
    new_jobs = []
    for job in jobs:
        try:
            cur.execute('''
                INSERT INTO oracle_dba_jobs (url, title, company, location)
                VALUES (?, ?, ?, ?)
            ''', (job['url'], job['title'], job['company'], job['location']))
            new_jobs.append(job)
        except sqlite3.IntegrityError:
            # Job URL already exists in database, skip it as duplicate
            pass
    conn.commit()
    conn.close()
    print(f"Saved {len(new_jobs)} new jobs to database '{db_name}'.")
    return new_jobs  # return only new jobs for emailing

def format_jobs_email(jobs):
    if not jobs:
        return "No new Oracle DBA job openings found today."
    lines = []
    for job in jobs:
        lines.append(f"Title: {job['title']}\nCompany: {job['company']}\nLocation: {job['location']}\nURL: {job['url']}\n")
    return "\n".join(lines)

def send_email(subject, body, sender_email, sender_password, recipient_email):
    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
    print(f"Job alert email sent to {recipient_email}.")

if __name__ == "__main__":
    jobs_list = scrape_indeed_jobs()
    new_jobs = save_jobs_to_sqlite(jobs_list)
    email_body = format_jobs_email(new_jobs)
    send_email(
        "Daily Oracle DBA Job Alerts - India",
        email_body,
        SENDER_EMAIL,
        SENDER_PASSWORD,
        RECIPIENT_EMAIL
    )
