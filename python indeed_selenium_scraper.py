import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_indeed_selenium():
    options = uc.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment to run headless

    driver = uc.Chrome(options=options)
    url = "https://in.indeed.com/jobs?q=oracle+dba&l=India"
    driver.get(url)
    print("Browser loaded URL.")

    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)

    # Always save the loaded page HTML for debugging
    with open("page_source_indeed.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved loaded page HTML to 'page_source_indeed.html'.")

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Directly target job titles by h2 with id or class containing 'JobInfoHeader-title'
    for job_title_tag in soup.find_all('h2', id='jobsearch-JobInfoHeader-title'):
        title = job_title_tag.get_text(strip=True)
        parent_div = job_title_tag.find_parent('div', class_='jobsearch-JobInfoHeader-title-container')

        # Find company/location below, typically in dedicated data-testid containers
        company = None
        location = None
        if parent_div:
            company_div = parent_div.find_next('div', attrs={'data-testid': 'jobsearch-CompanyInfoContainer'})
            if company_div:
                company = company_div.get_text(strip=True)
            location_div = parent_div.find_next('div', attrs={'data-testid': 'jobsearch-OtherJobDetailsContainer'})
            if location_div:
                location = location_div.get_text(strip=True)

        jobs.append({
            'title': title,
            'company': company if company else '',
            'location': location if location else ''
        })

    print(f"Extracted {len(jobs)} jobs using new selectors.")
    return jobs

if __name__ == "__main__":
    jobs = scrape_indeed_selenium()
    print(f"\nFound {len(jobs)} Oracle DBA jobs on Indeed:")
    for job in jobs[:5]:
        print(job)






