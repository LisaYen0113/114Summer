#twitter 特定人物頁面
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# 1. 設定 Chrome Driver
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 2. 打開 X 登入頁，請你手動登入
driver.get("https://twitter.com/login")
input("請登入完成後按 Enter 繼續...")

# 3. 登入後進入目標用戶頁面
target_url = "https://twitter.com/elonmusk"
driver.get(target_url)

# 4. 等待頁面動態內容載入
time.sleep(5)

# 5. 取得完整渲染後的 HTML
html = driver.page_source

# 6. 用 BeautifulSoup 解析
soup = BeautifulSoup(html, "html.parser")

# 7. 抓取推文主要內容
# X 的推文通常在 <article> 標籤內，內含 aria-label="Timeline: Your Home Timeline" 等屬性
tweets = soup.find_all("article")

print(f"找到 {len(tweets)} 篇推文")

for i, tweet in enumerate(tweets[:5], 1):  # 印前5篇推文
    # 推文文字通常在 <div> 中，class 會不斷變動，挑其中一種寫法：
    content_div = tweet.find("div", attrs={"data-testid": "tweetText"})
    if content_div:
        print(f"推文 {i}: {content_div.get_text(separator=' ', strip=True)}")
    else:
        print(f"推文 {i}: 找不到文字內容")

# 8. 關閉瀏覽器
driver.quit()
