#租租通
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get("https://www.dd-room.com/search")
time.sleep(3)  # 等待 JS 載入

soup = BeautifulSoup(driver.page_source, "html.parser")
# 然後一樣使用上方的解析邏輯

driver.quit()

# 抓取每筆物件卡片
items = soup.select("div.md\\:flex.md\\:py-6")  # 根據你給的範例

for i, item in enumerate(items[:10]):  # 只取前10筆作範例
    # 標題與連結
    title_tag = item.select_one("a.text-2xl")
    title = title_tag.text.strip() if title_tag else "無標題"
    relative_url = title_tag["href"] if title_tag else "#"
    full_url = "https://www.dd-room.com" + relative_url

    # 地址
    address_tag = item.select_one("div.flex.items-center.text-gray-500")
    address = address_tag.text.strip() if address_tag else "無地址"

    # 標籤（例如：可開伙、對外窗、有電梯…）
    tags = [span.text.strip() for span in item.select("div.line-clamp-1 span")]

    # 空間資訊（如：整層、3房1廳、28坪、5樓）
    detail_info = item.select_one("div.mt-2.text-gray-500")
    space_info = detail_info.text.strip() if detail_info else "無空間資訊"

    # 價格
    price_tag = item.select_one("span.text-xl, span.text-2xl")
    price = price_tag.text.strip() if price_tag else "無價格"

    # 圖片（第一張）
    img_tag = item.select_one(".swiper-slide-active img")
    img_url = img_tag.get("src") or img_tag.get("data-src")

    print(f"🏷️ 標題：{title}")
    print(f"📍 地址：{address}")
    print(f"📑 標籤：{'｜'.join(tags)}")
    print(f"🏠 空間：{space_info}")
    print(f"💰 租金：{price}")
    print(f"🖼️ 圖片：{img_url}")
    print(f"🔗 連結：{full_url}")
    print("-" * 40)
