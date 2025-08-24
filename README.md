# Oracle DBA Job Alert

A fully automated Python solution to aggregate Oracle DBA job postings from [Indeed India](https://in.indeed.com), persist new listings in a SQLite database, and send daily email notifications for the latest jobs. Run manually or schedule with cron for complete automation.

---

## Features

- **Multi-page scraping:** Collects jobs from several search result pages for broad coverage.
- **Smart de-duplication:** Saves only unique job listings using SQLite, preventing repeated alerts.
- **Automated daily email:** Sends a summary of new job openings to your inbox every morning.
- **Customizable:** Easily modify job search queries, number of pages scraped, and alert timing.
- **Error handling:** Outputs all script logs to a file for troubleshooting.
- **Easy scheduling:** Runs automatically via cron job on macOS or Linux.

---

## Setup Instructions

### 1. Clone the Repository
