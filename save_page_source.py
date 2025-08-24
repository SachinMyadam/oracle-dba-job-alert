import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_indeed_jobs():
    options = uc.ChromeOptions()
    # options.add_argument("--headless")

    driver = uc.Chrome(options=options)
    url = "https://in.indeed.com/jobs?q=oracle+dba&l=India"
    driver.get(url)
    print("Browser loaded URL.")

    # Scroll down to help load dynamic content
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)

    # Wait until job cards appear on the page (max 30 seconds)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
        )
        print("Job cards loaded.")
    except Exception as e:
        print("Timeout waiting for jobs:", e)

    # Save page source after jobs have loaded
    with open("page_source_indeed.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page source to 'page_source_indeed.html'.")

    driver.quit()

if __name__ == "__main__":
    scrape_indeed_jobs()



