# Google Maps 爬蟲程式

這個程式可以搜尋指定地址附近的設施，並獲取開車時間小於10分鐘的結果。

## 功能特色

- 自動搜尋指定地址
- 搜尋附近指定類型的設施
- 滑鼠懸浮獲取開車時間
- 篩選小於10分鐘的結果
- 將結果儲存為 JSON 格式

## 安裝需求

### 1. 安裝 Python 套件
```bash
pip install -r requirements.txt
```

### 2. 安裝 Chrome 瀏覽器
確保你的電腦已安裝 Google Chrome 瀏覽器

### 3. 安裝 ChromeDriver
有兩種方式：

**方式一：自動安裝（推薦）**
```python
# 修改 google_maps_crawler.py 中的 setup_driver 方法
from webdriver_manager.chrome import ChromeDriverManager

# 在 setup_driver 方法中替換為：
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

**方式二：手動安裝**
1. 下載 ChromeDriver：https://chromedriver.chromium.org/
2. 將 chromedriver.exe 放到系統 PATH 中，或指定路徑

## 使用方法

### 基本使用
```python
python google_maps_crawler.py
```

### 自訂參數
修改 `main()` 函數中的參數：
```python
address = "你的地址"
facility_type = "你要搜尋的設施類型"
```

## 輸出結果

程式會生成 `nearby_stations.json` 檔案，包含以下資訊：
```json
[
  {
    "設施名稱": "台中車站",
    "地址": "台中市中區台灣大道一段1號",
    "開車時間": "8分鐘",
    "時間(分鐘)": 8,
    "設施類型": "車站"
  }
]
```

## 注意事項

1. **網路連線**：確保網路連線穩定
2. **載入時間**：程式會等待頁面載入，請耐心等待
3. **反爬蟲機制**：如果遇到驗證碼，請手動處理後繼續
4. **使用頻率**：避免過於頻繁的請求，以免被封鎖

## 常見問題

### Q: ChromeDriver 版本不匹配
A: 使用 webdriver-manager 自動管理版本，或手動下載對應版本

### Q: 找不到元素
A: Google Maps 的頁面結構可能會變化，需要更新 XPath

### Q: 程式執行很慢
A: 這是正常現象，因為需要等待頁面載入和動畫效果

## 自訂設定

### 修改搜尋參數
```python
# 在 main() 函數中修改
address = "你的地址"
facility_type = "餐廳"  # 可以是：餐廳、醫院、學校、加油站等
```

### 修改時間篩選條件
```python
# 在 crawl_facilities 方法中修改
if travel_minutes and travel_minutes < 15:  # 改為15分鐘
```

### 無頭模式運行
```python
crawler = GoogleMapsCrawler(headless=True)
```