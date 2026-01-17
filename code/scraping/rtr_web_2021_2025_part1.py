"""
Pipeline step 1: Reuters DRC news ingestion

Purpose:
- Collect all Reuters articles mentioning the Democratic Republic of Congo (DRC)
- Extract title, publication date, and URL for downstream text analysis

Design choices:
- Use Selenium instead of requests due to Reuters' anti-bot measures
- Manual CAPTCHA handling to ensure data completeness
- No date filtering at this stage to preserve raw coverage

Output:
- CSV file with columns: title, date, url
— but this python script only scrapes the first 75 pages of the search results (75*20 = 1500 articles), and I used the 
  reuters_DRC_2022_24_v2.py script to scrape the remaining articles.
"""
# load libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import os

# Browser setup: initialize a Chrome WebDriver
def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    # prevent browser from opening after script finishes
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# Scrape Reuters DRC news
def scrape_reuters_drc():
    driver = setup_driver()
    all_articles = []
    
    url = "https://www.reuters.com/site-search/?query=democratic+republic+of+congo"
    driver.get(url)
    
    print("Please complete the CAPTCHA in the browser if prompted.")
    print("After completing the CAPTCHA, press Enter to continue...")
    input()
    
    page = 1
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        print(f"Scraping page {page}...")
        time.sleep(2 + random.uniform(1, 3))
        
        try:
            # Extract articles
            articles = driver.find_elements(By.CSS_SELECTOR, '[data-testid="StoryCard"]')
            
            if not articles:
                consecutive_errors += 1
                print(f"No articles found (error {consecutive_errors}/{max_errors})")
                if consecutive_errors >= max_errors:
                    break
                time.sleep(3)
                continue
            
            consecutive_errors = 0  # Reset error count
            
            for article in articles:
                try:
                    link_el = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleLink"]')
                    title_el = article.find_element(By.CSS_SELECTOR, '[data-testid="TitleHeading"]')
                    date_el = article.find_element(By.CSS_SELECTOR, 'time[data-testid="DateLineText"]')
                    
                    all_articles.append({
                        'title': title_el.text,
                        'date': date_el.get_attribute('datetime'),
                        'url': link_el.get_attribute('href')
                    })
                except:
                    continue
            
            print(f"  Found {len(articles)} articles, total: {len(all_articles)}")
            
            # Next page
            try:
                # Scroll to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Wait for button to be clickable
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="NextPageButton"]'))
                )
                
                # Check if disabled
                if next_btn.get_attribute('disabled'):
                    print("Reached last page")
                    break
                
                # Scroll to button position and click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(0.5)
                next_btn.click()
                page += 1
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                consecutive_errors += 1
                print(f"Next page error ({consecutive_errors}/{max_errors}): {e}")
                
                if consecutive_errors >= max_errors:
                    print("Too many errors, stopping")
                    break
                
                # Try refreshing page to retry
                time.sleep(3)
                continue
                
            if page > 150:
                print("Reached page limit")
                break
                
        except Exception as e:
            print(f"Error: {e}")
            consecutive_errors += 1
            if consecutive_errors >= max_errors:
                break
            time.sleep(3)
            continue
    
    driver.quit()

    # Save results to data/raw/ relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'rtr_web_2021_2025.csv')

    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=['url'])
    df.to_csv(csv_path, index=False)
    print(f"\nDone! Saved {len(df)} articles to {csv_path}")
    return df

# Main function to run the script
if __name__ == "__main__":
    scrape_reuters_drc()