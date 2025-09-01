import requests
from bs4 import BeautifulSoup
import csv
import json

# 假設這是列表頁 URL
url = "https://www.rakuya.com.tw/rent?search=city&city=0&page=1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

properties = []

for item in soup.select("div.obj-item"):
    title_tag = item.select_one("div.obj-title h6 a")
    address_tag = item.select_one("div.obj-title p.obj-address")
    price_tag = item.select_one("li.obj-price span")
    info_tags = item.select("ul.obj-data.clearfix li.clearfix span")
    icon_tags = item.select("ul.obj-icon.clearfix li svg")
    tag_tags = item.select("ul.obj-tag.clearfix li a")
    img_tag = item.select_one("a.obj-cover")
    
    # 抓取資料
    title = title_tag.text.strip() if title_tag else None
    link = title_tag['href'] if title_tag else None
    address = address_tag.text.strip() if address_tag else None
    price = price_tag.text.strip().replace("\n","") if price_tag else None
    
    layout = info_tags[1].text.strip() if len(info_tags) > 1 else None
    area = info_tags[2].text.strip() if len(info_tags) > 2 else None
    floor = info_tags[3].text.strip() if len(info_tags) > 3 else None
    
    # 標籤 / 特色
    features = [icon.get("title") for icon in icon_tags if icon.get("title")]
    tags = [t.text.strip() for t in tag_tags]
    
    # 圖片
    img_url = None
    if img_tag and 'style' in img_tag.attrs:
        style = img_tag['style']
        if "background-image" in style:
            start = style.find("url('") + 5
            end = style.find("')", start)
            img_url = style[start:end]
    
    properties.append({
        "title": title,
        "link": link,
        "address": address,
        "price": price,
        "layout": layout,
        "area": area,
        "floor": floor,
        "features": features,
        "tags": tags,
        "image": img_url
    })

# 存成 JSON
with open("properties.json", "w", encoding="utf-8") as f:
    json.dump(properties, f, ensure_ascii=False, indent=2)

# 存成 CSV
with open("properties.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=properties[0].keys())
    writer.writeheader()
    writer.writerows(properties)

print(f"抓取完成，共 {len(properties)} 筆物件")
