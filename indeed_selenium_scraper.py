import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_indeed_selenium():
    options = uc.ChromeOptions()
    # Uncomment to run headless (invisible browser)
    # options.add_argument("--headless")

    driver = uc.Chrome(options=options)
    url = "https://in.indeed.com/jobs?q=oracle+dba&l=India"
    driver.get(url)
    print("Browser loaded URL.")

    # Scroll down to load dynamic content
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
        )
        print("Job cards loaded.")
    except Exception as e:
        print("Timed out waiting for jobs:", e)
        with open("page_source_indeed.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page source to page_source_indeed.html")
        driver.quit()
        return []

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job_seen_beacon")
    jobs = []

    for c in cards:
        title_el = c.find("h2", class_="jobTitle")
        company_el = c.find("span", class_="companyName")
        location_el = c.find("div", class_="companyLocation")
        summary_el = c.find("div", class_="job-snippet")

        if title_el and company_el and location_el:
            job = {
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True),
                "location": location_el.get_text(strip=True),
                "summary": summary_el.get_text(strip=True) if summary_el else "",
            }
            jobs.append(job)

    return jobs

if __name__ == "__main__":
    jobs = scrape_indeed_selenium()
    print(f"Found {len(jobs)} Oracle DBA jobs on Indeed:")
    for job in jobs[:5]:
        print(job)


