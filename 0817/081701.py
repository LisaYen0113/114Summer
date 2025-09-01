from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 1. 登入 Facebook
driver.get("https://www.facebook.com/login")
input("請登入完成後按 Enter...")

# 2. 打開目標社團
target_url = "https://www.facebook.com/groups/1713612772170903"
driver.get(target_url)
time.sleep(5)

# 3. 滾動並邊抓文章
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")

all_texts = []

for _ in range(10):  # 可以調整滾動次數
    # 取得目前頁面的 HTML
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 找出可能的貼文
    posts1 = soup.find_all("div", {"data-ad-preview": "message"})
    posts2 = soup.find_all("div", {"dir": "auto"})
    all_posts = posts1 + posts2

    # 轉文字存起來
    texts = [p.get_text(separator="\n", strip=True) for p in all_posts if p.get_text(strip=True)]
    all_texts.extend(texts)

    # 滾動
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 4. 去重
all_texts_unique = list(dict.fromkeys(all_texts))

print(f"共抓到 {len(all_texts_unique)} 篇貼文")
for i, text in enumerate(all_texts_unique[:20], 1):
    print(f"貼文 {i}：\n{text}\n{'-'*40}")

driver.quit()
