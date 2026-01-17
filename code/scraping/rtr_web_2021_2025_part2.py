"""
Pipeline step 2: Reuters DRC news ingestion (continued)

Purpose:
- Continue scraping from the 76th page of the search results
- Extract title, publication date, and URL for downstream text analysis

Design choices:
- Use Selenium instead of requests due to Reuters' anti-bot measures
- Manual CAPTCHA handling to ensure data completeness
- No date filtering at this stage to preserve raw coverage

Output:
- CSV file with columns: title, date, url
- Merged with previous scrapes to ensure no duplicates
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
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# Scrape Reuters DRC news (continued)
def scrape_reuters_continue():
    driver = setup_driver()
    all_articles = []
    
    # Start from the 76th page (offset=1500)
    start_offset = 1500
    url = f"https://www.reuters.com/site-search/?query=democratic+republic+of+congo&offset={start_offset}"
    driver.get(url)
    
    print("Please complete the CAPTCHA in the browser if prompted.")
    print("After completing the CAPTCHA, press Enter to continue...")
    input()
    
    page = 76
    consecutive_errors = 0
    max_errors = 10
    
    while True:
        print(f"Scraping page {page}...")
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="StoryCard"]'))
            )
            time.sleep(1)
            
            articles = driver.find_elements(By.CSS_SELECTOR, '[data-testid="StoryCard"]')
            
            if not articles:
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    break
                driver.refresh()
                time.sleep(3)
                continue
            
            consecutive_errors = 0
            
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
            
            print(f"  Found {len(articles)}, total new: {len(all_articles)}")
            
            # Next page
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="NextPageButton"]'))
                )
                
                if next_btn.get_attribute('disabled'):
                    print("Reached last page")
                    break
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(0.5)
                next_btn.click()
                page += 1
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    break
                time.sleep(3)
                continue
                
            if page > 200:
                break
                
        except Exception as e:
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

    # Save new scraped articles
    df_new = pd.DataFrame(all_articles)
    part2_path = os.path.join(output_dir, 'rtr_web_2021_2025_part2.csv')
    df_new.to_csv(part2_path, index=False)
    print(f"\nSaved {len(df_new)} new articles to {part2_path}")

    # Merge with part1 articles
    try:
        part1_path = os.path.join(output_dir, 'rtr_web_2021_2025.csv')
        df_old = pd.read_csv(part1_path)
        df_all = pd.concat([df_old, df_new]).drop_duplicates(subset=['url'])
        merged_path = os.path.join(output_dir, 'rtr_web_2021_2025_merged.csv')
        df_all.to_csv(merged_path, index=False)
        print(f"Merged total: {len(df_all)} articles in {merged_path}")
    except:
        pass

    return df_new


if __name__ == "__main__":
    scrape_reuters_continue()

