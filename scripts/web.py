from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime

def scrape_blog(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(5)
        
        # Scroll to load more content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Extract blog posts
        posts = driver.find_elements(By.CSS_SELECTOR, 'article')  # Adjust selector as needed
        
        blog_data = []
        for post in posts:
            try:
                title = post.find_element(By.CSS_SELECTOR, 'h2').text
                content = post.find_element(By.CSS_SELECTOR, 'p').text
                date = post.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
                
                blog_data.append({
                    'title': title,
                    'content': content,
                    'date': date,
                    'url': url
                })
            except Exception as e:
                print(f"Error extracting post data: {str(e)}")
        
        return blog_data
    
    finally:
        driver.quit()

# List of Gen Z-related blog URLs to scrape
blogs = [
    "https://in.pinterest.com/Fashionfeedweb/gen-z-fashion/"
]

all_blog_data = []

for blog in blogs:
    print(f"Scraping: {blog}")
    blog_data = scrape_blog(blog)
    all_blog_data.extend(blog_data)

# Save data to JSON file
output_file = f"genz_blog_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_blog_data, f, ensure_ascii=False, indent=4)

print(f"Scraping completed! Data saved to {output_file}")