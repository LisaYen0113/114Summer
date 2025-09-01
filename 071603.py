#twitter查關鍵字並滾動頁面獲取更多
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

driver.get("https://twitter.com/login")
input("請登入完成後按 Enter 繼續...")

keyword = "台灣疫情"
search_url = f"https://twitter.com/search?q={keyword}&src=typed_query&f=live"
driver.get(search_url)
time.sleep(5)

# 模擬滾動多次，讓頁面載入更多推文
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(5):  # 滾動 5 次
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 取得滾動後的完整 HTML
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

tweets = soup.find_all("article")
print(f"滾動後找到 {len(tweets)} 篇推文")

for i, tweet in enumerate(tweets[:10], 1):
    content_div = tweet.find("div", attrs={"data-testid": "tweetText"})
    if content_div:
        print(f"推文 {i}: {content_div.get_text(separator=' ', strip=True)}")
    else:
        print(f"推文 {i}: 找不到文字內容")

driver.quit()
