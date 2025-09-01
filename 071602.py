#twittert查關鍵字
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

driver.get("https://twitter.com/login")
input("請登入完成後按 Enter 繼續...")

keyword = "台灣疫情"
search_url = "https://twitter.com/search?q=" + urllib.parse.quote(keyword) + "&src=typed_query&f=live"

driver.get(search_url)
time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

tweets = soup.find_all("article")
print(f"找到 {len(tweets)} 篇推文")

for i, tweet in enumerate(tweets[:5], 1):
    content_div = tweet.find("div", attrs={"data-testid": "tweetText"})
    if content_div:
        print(f"推文 {i}: {content_div.get_text(separator=' ', strip=True)}")
    else:
        print(f"推文 {i}: 找不到文字內容")

driver.quit()
