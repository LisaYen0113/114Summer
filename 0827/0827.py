import requests

url = "https://buy.yungching.com.tw/api/v2/recommend/listpromote"  # 這裡要換成實際在 Network 看到的 API
params = {
    "city": "台北市",
    "pg": 1
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()

for house in data.get("result", []):
    print(house.get("caseName"), house.get("price"), house.get("area"))
