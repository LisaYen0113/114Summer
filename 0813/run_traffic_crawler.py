#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通資訊爬蟲執行腳本
使用配置文件來設定參數和篩選條件
"""

import json
import sys
from traffic_info_crawler import TrafficInfoCrawler


def load_config(config_file="traffic_config.json"):
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


def prepare_filters(filter_config):
    """準備篩選條件"""
    active_filters = {}
    
    for filter_name, filter_settings in filter_config.items():
        if filter_settings.get('啟用', False):
            active_filters[filter_name] = {
                '交通方式': filter_settings['交通方式'],
                '最大時間_分鐘': filter_settings['最大時間_分鐘']
            }
    
    return active_filters


def main():
    """主函數"""
    print("=== 交通資訊爬蟲程式 ===")
    
    # 載入配置
    config = load_config()
    if not config:
        print("使用預設設定...")
        config = {
            "檔案設定": {
                "輸入檔案": "nearby_車站.json",
                "輸出檔案": "facilities_with_traffic.json"
            },
            "搜尋設定": {
                "起始地址": "臺中市北區三民路三段",
                "是否按距離排序": True,
                "處理延遲秒數": 3
            },
            "篩選條件": {
                "大眾運輸篩選": {
                    "啟用": True,
                    "交通方式": "大眾運輸",
                    "最大時間_分鐘": 15
                }
            },
            "瀏覽器設定": {
                "無頭模式": False,
                "等待時間_秒": 20
            }
        }
    
    # 取得設定
    file_config = config["檔案設定"]
    search_config = config["搜尋設定"]
    filter_config = config["篩選條件"]
    browser_config = config["瀏覽器設定"]
    
    input_file = file_config["輸入檔案"]
    output_file = file_config["輸出檔案"]
    start_address = search_config["起始地址"]
    headless = browser_config["無頭模式"]
    
    # 準備篩選條件
    filters = prepare_filters(filter_config)
    
    print(f"輸入檔案: {input_file}")
    print(f"輸出檔案: {output_file}")
    print(f"起始地址: {start_address}")
    print(f"無頭模式: {'是' if headless else '否'}")
    print(f"啟用的篩選條件:")
    
    if filters:
        for filter_name, filter_data in filters.items():
            original_config = filter_config[filter_name]
            print(f"  - {filter_data['交通方式']}: 最大 {filter_data['最大時間_分鐘']} 分鐘")
            if '說明' in original_config:
                print(f"    ({original_config['說明']})")
    else:
        print("  - 無篩選條件")
    
    print("=" * 60)
    
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
    crawler = TrafficInfoCrawler(headless=headless)
    
    try:
        # 載入設施資料
        print(f"\n正在載入設施資料: {input_file}")
        facilities = crawler.load_facilities_json(input_file)
        
        if not facilities:
            print("沒有設施資料可處理")
            return
        
        print(f"載入了 {len(facilities)} 個設施")
        
        # 顯示設施列表
        print("\n設施列表:")
        for i, facility in enumerate(facilities, 1):
            print(f"  {i}. {facility['設施名稱']} - {facility['地址']}")
        
        # 處理設施
        print(f"\n開始處理設施...")
        crawler.process_facilities(facilities, start_address, filters)
        
        # 儲存結果
        crawler.save_results(output_file)
        
        if crawler.results:
            print(f"\n✓ 成功處理 {len(crawler.results)} 個設施")
            print(f"✓ 結果已儲存到 {output_file}")
        else:
            print("\n⚠ 沒有設施通過篩選條件")
        
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