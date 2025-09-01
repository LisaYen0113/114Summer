import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    for item in soup.find_all("div", class_="obj-item"):
        title_element = item.select_one(".obj-title h6 a")
        title = title_element.text.strip() if title_element else "N/A"
        price_element = item.select_one(".obj-price span")
        price = price_element.text.strip() if price_element else "N/A"
        address_element = item.select_one(".obj-address")
        address = address_element.text.strip() if address_element else "N/A"
        if title != 'N/A': # 只添加有效的物件
            listings.append({"title": title, "price": price, "address": address})
    return listings

if __name__ == '__main__':
    base_url = "https://www.rakuya.com.tw/rent?search=city&city=1&page="
    all_listings = []
    for page_num in range(1, 250):
        url = f"{base_url}{page_num}"
        print(f"Scraping {url}")
        listings = scrape_page(url)
        all_listings.extend(listings)

    df = pd.DataFrame(all_listings)
    df.to_csv("rakuya_rentals.csv", index=False, encoding="utf-8-sig")
    print("Scraping complete. Data saved to rakuya_rentals.csv")