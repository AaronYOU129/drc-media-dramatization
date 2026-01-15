"""
Selenium 爬取 Reuters DRC 新闻
pip install selenium webdriver-manager pandas
"""

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

def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    # options.add_experimental_option("detach", True)  # 取消注释则脚本结束后浏览器不关闭
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_reuters_drc():
    driver = setup_driver()
    all_articles = []
    
    url = "https://www.reuters.com/site-search/?query=democratic+republic+of+congo"
    driver.get(url)
    
    print("请在浏览器中完成人机验证（如果有的话）")
    print("完成后按 Enter 继续...")
    input()
    
    page = 1
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        print(f"Scraping page {page}...")
        time.sleep(2 + random.uniform(1, 3))
        
        try:
            # 提取文章
            articles = driver.find_elements(By.CSS_SELECTOR, '[data-testid="StoryCard"]')
            
            if not articles:
                consecutive_errors += 1
                print(f"No articles found (error {consecutive_errors}/{max_errors})")
                if consecutive_errors >= max_errors:
                    break
                time.sleep(3)
                continue
            
            consecutive_errors = 0  # 重置错误计数
            
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
            
            # 翻页
            try:
                # 滚动到底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # 等待按钮可点击
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="NextPageButton"]'))
                )
                
                # 检查是否disabled
                if next_btn.get_attribute('disabled'):
                    print("Reached last page")
                    break
                
                # 滚动到按钮位置并点击
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
                
                # 尝试刷新页面重试
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
    
    # 保存结果
    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=['url'])
    df.to_csv('reuters_drc_selenium.csv', index=False)
    print(f"\nDone! Saved {len(df)} articles to reuters_drc_selenium.csv")
    return df


if __name__ == "__main__":
    scrape_reuters_drc()