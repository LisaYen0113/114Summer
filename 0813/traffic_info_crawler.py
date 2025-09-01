#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通資訊爬蟲程式
讀取設施 JSON 檔案，逐一搜尋每個設施的交通資訊
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class TrafficInfoCrawler:
    def __init__(self, headless=False):
        """
        初始化交通資訊爬蟲
        
        Args:
            headless (bool): 是否使用無頭模式
        """
        self.driver = None
        self.wait = None
        self.results = []
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """設置 Chrome 瀏覽器"""
        print("正在設置瀏覽器...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # 基本設定
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 設定 User-Agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            print("瀏覽器設置完成")
            
        except Exception as e:
            print(f"設置瀏覽器時發生錯誤: {e}")
            raise
    
    def load_facilities_json(self, json_file):
        """載入設施 JSON 檔案"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                facilities = json.load(f)
            print(f"成功載入 {len(facilities)} 個設施資料")
            return facilities
        except FileNotFoundError:
            print(f"找不到檔案: {json_file}")
            return []
        except json.JSONDecodeError:
            print(f"JSON 檔案格式錯誤: {json_file}")
            return []
    
    def search_facility_directions(self, start_address, facility_name, facility_address):
        """搜尋從起始地址到設施的路線資訊"""
        print(f"正在搜尋路線: {start_address} → {facility_name}")
        
        try:
            # 開啟 Google Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(2)  # 減少等待時間
            
            # 先在搜尋框輸入起始地址
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(start_address)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)  # 減少等待時間
            
            # 點擊規劃路線按鈕 - 嘗試多種選擇器
            directions_selectors = [
                "//button[@data-value='規劃路線']",
                "//button[@aria-label='規劃路線']",
                "//button[contains(@class, 'g88MCb') and @data-value='規劃路線']",
                "//button[@data-value='Directions']",
                "//button[contains(@aria-label, '路線')]",
                "//button[contains(text(), '路線')]",
                "//button[contains(text(), '規劃路線')]",
                "//div[@data-value='規劃路線']",
                "//div[@data-value='Directions']"
            ]
            
            directions_button = None
            for selector in directions_selectors:
                try:
                    directions_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not directions_button:
                print("找不到路線按鈕")
                return False
                
            directions_button.click()
            time.sleep(2)  # 減少等待時間
            
            # 在規劃路線的輸入框中填入設施資訊
            route_input_selectors = [
                "//input[@class='tactile-searchbox-input']",
                "//input[contains(@aria-label, '起點')]",
                "//input[@placeholder='']",
                "//input[contains(@class, 'tactile-searchbox-input')]"
            ]
            
            route_input = None
            for selector in route_input_selectors:
                try:
                    route_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not route_input:
                print("找不到路線輸入框")
                return False
            
            # 完全清空輸入框（包括之前的內容）
            route_input.click()  # 確保焦點在輸入框上
            time.sleep(0.5)
            
            # 全選並刪除現有內容
            route_input.send_keys(Keys.CONTROL + "a")  # 全選
            time.sleep(0.5)
            route_input.send_keys(Keys.DELETE)  # 刪除
            time.sleep(0.5)
            
            # 再次嘗試清空
            route_input.clear()
            time.sleep(1)
            
            # 填入新的設施資訊
            facility_search_text = f"{facility_name} {facility_address}"
            print(f"  填入搜尋內容: {facility_search_text}")
            
            route_input.send_keys(facility_search_text)
            route_input.send_keys(Keys.RETURN)
            
            # 等待路線計算完成
            time.sleep(5)  # 減少等待時間
            
            return True
            
        except Exception as e:
            print(f"搜尋路線時發生錯誤: {e}")
            return False
    
    def click_sort_by_distance(self):
        """點擊按距離排序（已停用）"""
        # 不需要距離排序，直接返回 True
        print("  跳過距離排序")
        return True
    
    def extract_traffic_info(self):
        """提取所有交通方式的時間資訊"""
        traffic_info = {}
        
        try:
            # 等待路線資訊載入（減少等待時間）
            time.sleep(3)
            
            # 尋找所有交通方式按鈕
            transport_buttons = self.driver.find_elements(By.XPATH, "//button[@class='m6Uuef']")
            
            print(f"  找到 {len(transport_buttons)} 個交通方式按鈕")
            
            for i, button in enumerate(transport_buttons):
                try:
                    # 獲取交通方式名稱
                    transport_type = button.get_attribute('data-tooltip')
                    if not transport_type:
                        # 如果沒有 data-tooltip，嘗試從 aria-label 獲取
                        transport_type = button.find_element(By.XPATH, ".//div[@role='img']").get_attribute('aria-label')
                    
                    # 獲取時間資訊
                    time_element = button.find_element(By.XPATH, ".//div[@class='Fl2iee HNPWFe']")
                    time_text = time_element.text.strip()
                    
                    if transport_type and time_text:
                        traffic_info[transport_type] = time_text
                        print(f"  {transport_type}: {time_text}")
                    
                except Exception as e:
                    print(f"  處理第 {i+1} 個交通方式按鈕時發生錯誤: {e}")
                    continue
            
            return traffic_info
            
        except Exception as e:
            print(f"提取交通資訊時發生錯誤: {e}")
            return {}
    
    def extract_traffic_info_fallback(self):
        """備用的交通資訊提取方法"""
        traffic_info = {}
        
        try:
            # 備用選擇器
            fallback_selectors = [
                "//div[contains(@class, 'Fl2iee') and contains(@class, 'HNPWFe')]",
                "//span[contains(text(), '分') or contains(text(), '時')]",
                "//div[contains(text(), '分鐘') or contains(text(), '小時')]"
            ]
            
            for selector in fallback_selectors:
                try:
                    time_elements = self.driver.find_elements(By.XPATH, selector)
                    for i, element in enumerate(time_elements):
                        text = element.text.strip()
                        if self.is_time_text(text):
                            # 嘗試找到對應的交通方式
                            parent = element.find_element(By.XPATH, "./ancestor::button")
                            transport_type = parent.get_attribute('data-tooltip')
                            if not transport_type:
                                transport_type = f"交通方式{i+1}"
                            
                            traffic_info[transport_type] = text
                            break
                except:
                    continue
            
            return traffic_info
            
        except Exception as e:
            print(f"備用提取方法發生錯誤: {e}")
            return {}
    
    def is_time_text(self, text):
        """判斷文字是否為時間格式"""
        time_patterns = [
            r'\d+\s*分鐘',
            r'\d+\s*小時',
            r'\d+\s*時',
            r'\d+\s*分',
            r'\d+\s*min',
            r'\d+\s*hour',
            r'\d+\s*hr'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def apply_filters(self, facility_data, filters):
        """
        應用篩選條件
        
        Args:
            facility_data (dict): 設施資料
            filters (dict): 篩選條件
        
        Returns:
            bool: True 保留，False 刪除
        """
        try:
            traffic_info = facility_data.get('交通資訊', {})
            
            # 在這裡添加你的篩選邏輯
            for filter_name, filter_config in filters.items():
                transport_type = filter_config.get('交通方式')
                max_time = filter_config.get('最大時間_分鐘')
                
                if transport_type in traffic_info:
                    time_text = traffic_info[transport_type]
                    time_minutes = self.extract_minutes_from_text(time_text)
                    
                    if time_minutes and time_minutes > max_time:
                        print(f"  ✗ 篩選掉: {facility_data['設施名稱']} - {transport_type} {time_minutes}分鐘 > {max_time}分鐘")
                        return False
            
            return True
            
        except Exception as e:
            print(f"應用篩選條件時發生錯誤: {e}")
            return True
    
    def extract_minutes_from_text(self, time_text):
        """從時間文字中提取分鐘數"""
        try:
            # 提取小時和分鐘
            hour_match = re.search(r'(\d+)\s*小時', time_text)
            min_match = re.search(r'(\d+)\s*分', time_text)
            
            total_minutes = 0
            if hour_match:
                total_minutes += int(hour_match.group(1)) * 60
            if min_match:
                total_minutes += int(min_match.group(1))
            
            return total_minutes if total_minutes > 0 else None
            
        except Exception:
            return None
    
    def process_facilities(self, facilities, start_address, filters=None):
        """處理所有設施，獲取交通資訊"""
        if filters is None:
            filters = {}
        
        print(f"開始處理 {len(facilities)} 個設施...")
        
        for i, facility in enumerate(facilities, 1):
            try:
                print(f"\n處理第 {i}/{len(facilities)} 個設施: {facility['設施名稱']}")
                
                # 搜尋路線
                success = self.search_facility_directions(
                    start_address, 
                    facility['設施名稱'], 
                    facility['地址']
                )
                
                if not success:
                    print(f"  ✗ 跳過: 無法搜尋路線")
                    continue
                
                # 提取交通資訊（不需要距離排序）
                traffic_info = self.extract_traffic_info()
                
                if not traffic_info:
                    print(f"  ✗ 跳過: 無法獲取交通資訊")
                    continue
                
                # 將交通資訊加入設施資料
                facility_with_traffic = facility.copy()
                facility_with_traffic['交通資訊'] = traffic_info
                
                # 應用篩選條件
                if self.apply_filters(facility_with_traffic, filters):
                    self.results.append(facility_with_traffic)
                    print(f"  ✓ 已加入結果")
                else:
                    print(f"  ✗ 被篩選條件排除")
                
            except Exception as e:
                print(f"  ✗ 處理設施時發生錯誤: {e}")
                # 不要 continue，直接處理下一個設施
        
        print(f"\n處理完成，共保留 {len(self.results)} 個設施")
    
    def save_results(self, filename="facilities_with_traffic.json"):
        """儲存結果到 JSON 檔案"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n結果已儲存到 {filename}")
            
            # 顯示結果摘要
            if self.results:
                print("\n=== 結果摘要 ===")
                for i, result in enumerate(self.results, 1):
                    print(f"{i}. {result['設施名稱']}")
                    traffic_info = result.get('交通資訊', {})
                    for transport, time_info in traffic_info.items():
                        print(f"   {transport}: {time_info}")
            
        except Exception as e:
            print(f"儲存檔案時發生錯誤: {e}")
    
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            print("瀏覽器已關閉")


def main():
    """主函數"""
    # 設定參數
    input_json_file = "nearby_車站.json"  # 輸入的設施 JSON 檔案
    start_address = "臺中市北區三民路三段"  # 起始地址
    output_file = "facilities_with_traffic.json"  # 輸出檔案
    
    # 篩選條件設定區域 - 你可以在這裡修改篩選條件
    filters = {
        "大眾運輸篩選": {
            "交通方式": "大眾運輸",
            "最大時間_分鐘": 15  # 大眾運輸超過15分鐘就刪除
        }
        # 可以添加更多篩選條件，例如：
        # "開車篩選": {
        #     "交通方式": "開車",
        #     "最大時間_分鐘": 30
        # }
    }
    
    print("=== 交通資訊爬蟲程式 ===")
    print(f"輸入檔案: {input_json_file}")
    print(f"起始地址: {start_address}")
    print(f"輸出檔案: {output_file}")
    print(f"篩選條件: {filters}")
    print("=" * 50)
    
    # 創建爬蟲實例
    crawler = TrafficInfoCrawler(headless=False)
    
    try:
        # 載入設施資料
        facilities = crawler.load_facilities_json(input_json_file)
        
        if not facilities:
            print("沒有設施資料可處理")
            return
        
        # 處理設施
        crawler.process_facilities(facilities, start_address, filters)
        
        # 儲存結果
        crawler.save_results(output_file)
        
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        crawler.close()


if __name__ == "__main__":
    main()