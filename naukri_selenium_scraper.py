import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_naukri_undetected(url):
    options = uc.ChromeOptions()
    # Optional: Run headless (can try removing headless if still blocked)
    # options.add_argument("--headless")

    driver = uc.Chrome(options=options)
    driver.get(url)
    print("Browser loaded URL.")

    # Scroll down to load jobs
    total_scrolls = 5
    scroll_pause_time = 2
    for i in range(total_scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        print(f"Scrolled down {i + 1} times")
        time.sleep(scroll_pause_time)

    # Wait for job listings container
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.jobTuple"))
        )
        print("Job tuple elements found on page.")
    except Exception as e:
        print("Timed out waiting for job listings:", e)
        with open("page_source_undetected.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page source to page_source_undetected.html for inspection.")
        driver.quit()
        return []

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.jobTuple")
    print(f"Total job cards found: {len(cards)}")

    jobs = []
    for c in cards:
        try:
            title_el = c.select_one("a.title")
            comp_el = c.select_one("a.comp-name")
            loc_el = c.select_one("span.locWdth")

            title = title_el.get_text(strip=True) if title_el else ''
            company = comp_el.get_text(strip=True) if comp_el else ''
            location = loc_el.get_text(strip=True) if loc_el else ''

            print(f"Job card title: {title}")

            if 'oracle' in title.lower() and 'dba' in title.lower():
                print("Oracle DBA job found!")
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                })
        except Exception as e:
            print(f"Error parsing job card: {e}")

    print(f"Returning {len(jobs)} Oracle DBA jobs.")
    return jobs

if __name__ == "__main__":
    url = "https://www.naukri.com/oracle-dba-jobs"
    jobs = scrape_naukri_undetected(url)
    print(f"Found {len(jobs)} Oracle DBA jobs on Naukri:")
    for job in jobs[:5]:
        print(job)
