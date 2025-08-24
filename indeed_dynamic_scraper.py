from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

def scrape_indeed_jobs():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    url = "https://in.indeed.com/jobs?q=oracle+dba&l=India"
    driver.get(url)
    print("Browser loaded URL.")

    time.sleep(3)

    # Wait for job cards container to load
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

if __name__ == "__main__":
    jobs_list = scrape_indeed_jobs()
    print(f"Found {len(jobs_list)} jobs:")
    for job in jobs_list[:10]:
        print(job)
