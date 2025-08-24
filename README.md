# Oracle DBA Job Alert

Automated Python scraper that collects Oracle DBA job openings from Indeed India, saves new listings to an SQLite database, and sends daily email alerts with job updates. Scheduled to run daily using a cron job on macOS.

## Features

- Scrapes multiple pages of job listings using Selenium with undetected-chromedriver.
- Saves unique job postings in SQLite database to avoid duplicates.
- Sends daily email notifications with new job openings.
- Easily scheduled with a cron job for regular automated execution.

## Setup

1. Clone the repo:
