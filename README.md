cat > README.md <<EOF

# Oracle DBA Job Alert

A fully automated Python solution to aggregate Oracle DBA job postings from [Indeed India](https://in.indeed.com), persist new listings in a SQLite database, and send daily email notifications for the latest jobs. Run manually or schedule with cron for complete automation.

---

## Table of Contents

- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Configuration](#configuration)
- [Automation](#automation)
- [Database](#database)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- Multi-page scraping for comprehensive job listings.
- Smart de-duplication using SQLite database to avoid repeats.
- Automated daily email alerts summarizing new openings.
- Easily customizable search queries and alert timing.
- Error logging for troubleshooting.
- Supports scheduling with cron on macOS/Linux.

---

## Setup Instructions

1. Clone the repository:

   \`\`\`sh
   git clone https://github.com/SachinMyadam/oracle-dba-job-alert.git
   cd oracle-dba-job-alert
   \`\`\`

2. Create a Python virtual environment and activate it:

   \`\`\`sh
   python3.11 -m venv .venv
   source .venv/bin/activate
   \`\`\`

3. Install dependencies:

   \`\`\`sh
   pip install --upgrade pip
   pip install -r requirements.txt
   \`\`\`

---

## Usage

Run the scraper manually:

\`\`\`sh
python daily_oracle_dba_job_alert.py
\`\`\`

Check your email for alerts with the latest Oracle DBA jobs.

---

## Configuration

- Modify email settings and job search parameters inside \`daily_oracle_dba_job_alert.py\`.
- Customize alert timings or add new job boards as needed.

---

## Automation

Set up cron to run the script daily:

\`\`\`sh
crontab -e
\`\`\`

Add:

\`\`\`
0 8 \* \* \* /path/to/.venv/bin/python /path/to/daily_oracle_dba_job_alert.py >> /path/to/cronjob.log 2>&1
\`\`\`

---

## Database

The script stores jobs in \`jobs.db\` SQLite file to track and avoid duplicate alerts.

---

## Error Handling

Script logs errors and execution details to \`oracle_dba_scraper.log\` for debugging.

---

## Contributing

Contributions welcome! Open issues or submit pull requests.

---

## License

MIT License — see LICENSE file.

---

## Contact

Sachin Myadam  
Email: nanisachin45@gmail.com  
GitHub: [https://github.com/SachinMyadam](https://github.com/SachinMyadam)
EOF
