from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

def google_trend_buyhouse(location: str):
    # 初始化 pytrends
    pytrends = TrendReq(hl='zh-TW', tz=480)

    # 關鍵字，例如「買房 台中」
    keyword = f"買房 {location}"

    # 建立 payload，地區限定台灣，時間範圍一年內
    pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='TW', gprop='')

    # 抓取趨勢資料
    data = pytrends.interest_over_time()

    if data.empty:
        print(f"⚠️ 沒有找到 '{keyword}' 的趨勢資料")
        return

    # 繪圖
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data[keyword], label=keyword, linewidth=2)
    plt.title(f"Google Trends：{keyword}（過去一年，台灣）", fontsize=14)
    plt.xlabel("日期")
    plt.ylabel("熱度指數")
    plt.legend()
    plt.grid(True)
    plt.show()

    return data

# 範例：查詢台中的「買房 台中」
df = google_trend_buyhouse("台中")

# 如果要輸出數據表格
if df is not None:
    print(df.head())
