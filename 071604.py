# FB 不完整但有成功 (沒成功 貼文是斷的)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 1. 打開 FB 登入頁，手動登入
driver.get("https://www.facebook.com/login")
input("請登入完成後按 Enter...")

# 2. 打開目標社團
target_url = "https://www.facebook.com/groups/1713612772170903"
driver.get(target_url)

# 等待「文章區塊」載入（用 role="article" 比較穩定）
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="article"]'))
    )
except:
    print("等不到社團文章載入")
    driver.quit()
    exit()

# 3. 模擬滾動多次，載入更多貼文
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 4. 取得頁面 HTML 並用 BeautifulSoup 解析
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 5. 找出所有貼文內容（文章的文字通常在 data-ad-preview="message"）
posts = soup.find_all("div", {"data-ad-preview": "message"})

if posts:
    print(f"找到 {len(posts)} 篇貼文")
    for i, post in enumerate(posts[:5], 1):  # 只列前 5 篇
        text = post.get_text(separator="\n", strip=True)
        print(f"貼文 {i} 內容：\n{text}\n{'-'*40}")
else:
    print("找不到貼文內容")

driver.quit()
