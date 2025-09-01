from pytrends.request import TrendReq
import pandas as pd

# 初始化 API
pytrends = TrendReq(hl="zh-TW", tz=480, retries=3, backoff_factor=0.5)

# 設定關鍵字
keywords = ["地震"]

# 設定時間範圍：2020-07-18 到今天
timeframe = "2020-07-18 2025-08-18"

# 建立查詢
pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo="TW")

# 取得各城市（縣市）數據
trend_city = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=False)

# 輸出 CSV
trend_city.to_csv("taiwan_earthquake_trend_by_city.csv", encoding="utf-8-sig")

print("已成功匯出：taiwan_earthquake_trend_by_city.csv")
