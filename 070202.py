#民視結巴斷詞

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

import jieba
import csv

options = Options()
# options.add_argument("--headless")  # 若不需看到畫面可打開這行（抓資料更快，但不利 debug）
options.add_argument("--ignore-certificate-errors")
options.add_argument("--no-proxy-server")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.get("https://www.ftvnews.com.tw/realtime/")

# 模擬向下捲動頁面（共捲 5 次）
for _ in range(1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #用 JavaScript 模擬瀏覽器滾動到底部
    time.sleep(1) #等待每次滾動後的新聞載入

soup = BeautifulSoup(driver.page_source, "html.parser")
news_cards = soup.select(".news-block")

print("共抓到新聞：", len(news_cards))
print("-" * 40)

for card in news_cards[:10]:  # 取前10筆
    title = card.select_one("h2.title").text.strip() #.text.strip() 是去除前後空白
    time_text = card.select_one("div.time").text.strip()
    desc = card.select_one("div.desc").text.strip()
    relative_url = card.select_one("a[href]")["href"]
    full_url = "https://www.ftvnews.com.tw" + relative_url

    print("📰 標題：", title)
    print("🕒 時間：", time_text)
    print("📄 摘要：", desc)
    print("🔗 連結：", full_url)

    # 開新分頁打開文章連結
    driver.get(full_url)
    time.sleep(1.5)  # 保守等待內頁載入（可調整）

    detail_soup = BeautifulSoup(driver.page_source, "html.parser")
    content_div = detail_soup.select_one("#preface")

    if content_div:
        paragraphs = content_div.find_all("p")
        article = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        print("📜 內文：", article)
    else:
        print("⚠️ 找不到內文")
    
    print("-" * 40)
    
    tokens = jieba.lcut(article)  # 精確模式
    # 或 jieba.cut(article, cut_all=True) # 全模式（比較粗糙）
    # 把斷詞結果存成一行（以空格分隔）
    segmented_text = ','.join(tokens)
     # 儲存成 CSV 檔（每一列一篇文章）
    with open("news_cut.csv", "a", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([title, segmented_text])

        
driver.quit()
