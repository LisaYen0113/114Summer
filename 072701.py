import requests

class House591Spider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://rent.591.com.tw/",
        }

    def search(self, region=6, first_row=0):
        """搜尋指定區域，回傳 JSON"""
        url = "https://bff.591.com.tw/v1/house/rent/list"
        params = {
            "is_format_data": 1,
            "region": region,   # 6 = 桃園市
            "firstRow": first_row,
            "totalRows": 0
        }

        res = self.session.get(url, headers=self.headers, params=params)
        res.raise_for_status()
        data = res.json()

        # 取出每個物件 ID
        houses = [item["post_id"] for item in data["data"]["data"]]
        return houses

if __name__ == "__main__":
    spider = House591Spider()
    houses = spider.search(region=6, first_row=0)  # 抓桃園市第一頁 (30 筆)
    print(f"找到 {len(houses)} 間房屋")
    print("房屋 ID：", houses)
