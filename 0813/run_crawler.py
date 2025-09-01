#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps 爬蟲執行腳本
使用配置文件來設定參數
"""

import json
import sys
from google_maps_crawler_improved import GoogleMapsCrawler


def load_config(config_file="config.json"):
    """載入配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"找不到配置文件: {config_file}")
        return None
    except json.JSONDecodeError:
        print(f"配置文件格式錯誤: {config_file}")
        return None


def main():
    """主函數"""
    print("=== Google Maps 爬蟲程式 ===")
    
    # 載入配置
    config = load_config()
    if not config:
        print("使用預設設定...")
        config = {
            "搜尋設定": {
                "地址": "臺中市北區三民路三段",
                "設施類型": "車站",
                "最大結果數量": 15
            },
            "瀏覽器設定": {
                "無頭模式": False,
                "等待時間_秒": 20,
                "頁面載入延遲_秒": 3
            },
            "輸出設定": {
                "檔案名稱": "nearby_facilities.json",
                "顯示詳細日誌": True
            }
        }
    
    # 取得設定
    search_config = config["搜尋設定"]
    browser_config = config["瀏覽器設定"]
    output_config = config["輸出設定"]
    
    address = search_config["地址"]
    facility_type = search_config["設施類型"]
    max_results = search_config["最大結果數量"]
    headless = browser_config["無頭模式"]
    output_file = output_config["檔案名稱"]
    
    print(f"搜尋地址: {address}")
    print(f"設施類型: {facility_type}")
    print(f"最大結果數量: {max_results}")
    print(f"無頭模式: {'是' if headless else '否'}")
    print(f"輸出檔案: {output_file}")
    print("=" * 50)
    
    # 詢問是否繼續
    try:
        user_input = input("按 Enter 開始執行，或輸入 'q' 退出: ").strip().lower()
        if user_input == 'q':
            print("程式已退出")
            return
    except KeyboardInterrupt:
        print("\n程式已退出")
        return
    
    # 創建爬蟲實例
    crawler = GoogleMapsCrawler(headless=headless)
    
    try:
        # 執行爬蟲
        print("\n開始執行爬蟲...")
        success = crawler.crawl_facilities(address, facility_type)
        
        if success:
            # 儲存結果
            crawler.save_results(output_file)
            
            if crawler.results:
                print(f"\n✓ 成功找到 {len(crawler.results)} 個符合條件的設施")
                print(f"✓ 結果已儲存到 {output_file}")
            else:
                print("\n⚠ 沒有找到符合條件的設施")
        else:
            print("\n✗ 爬蟲執行失敗")
    
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"\n執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        crawler.close()
        print("\n程式執行完畢")


if __name__ == "__main__":
    main()