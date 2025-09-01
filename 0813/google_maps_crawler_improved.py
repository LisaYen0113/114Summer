#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps 爬蟲程式 - 改進版
功能：搜尋指定地址附近的設施，並獲取開車時間小於指定時間的結果
使用 webdriver-manager 自動管理 ChromeDriver
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


class GoogleMapsCrawler:
    def __init__(self, headless=False):
        """
        初始化爬蟲
        
        Args:
            headless (bool): 是否使用無頭模式
        """
        self.driver = None
        self.wait = None
        self.results = []
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """設置 Chrome 瀏覽器，使用 webdriver-manager 自動管理"""
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
            # 使用 webdriver-manager 自動下載和管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 隱藏自動化特徵
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            print("瀏覽器設置完成")
            
        except Exception as e:
            print(f"設置瀏覽器時發生錯誤: {e}")
            raise
    
    def search_address(self, address):
        """搜尋地址"""
        print(f"正在搜尋地址: {address}")
        
        try:
            # 開啟 Google Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(3)
            
            # 找到搜尋框並輸入地址
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(address)
            search_box.send_keys(Keys.RETURN)
            
            # 等待搜尋結果載入
            time.sleep(5)
            print(f"地址搜尋完成: {address}")
            return True
            
        except TimeoutException:
            print("搜尋地址時發生超時錯誤")
            return False
        except Exception as e:
            print(f"搜尋地址時發生錯誤: {e}")
            return False
    
    def search_nearby_facilities(self, facility_name):
        """搜尋附近設施"""
        print(f"正在搜尋附近設施: {facility_name}")
        
        try:
            # 嘗試多種方式找到附近按鈕
            nearby_selectors = [
                "//button[@data-value='附近']",
                "//button[@data-value='Nearby']",
                "//button[contains(@class, 'g88MCb') and @data-value='附近']",
                "//button[contains(text(), '附近')]",
                "//button[contains(text(), 'Nearby')]",
                "//div[@data-value='附近']",
                "//div[@data-value='Nearby']"
            ]
            
            nearby_button = None
            for selector in nearby_selectors:
                try:
                    nearby_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not nearby_button:
                print("找不到附近按鈕，嘗試直接搜尋")
                return self.direct_search_nearby(facility_name)
            
            nearby_button.click()
            time.sleep(3)
            
            # 尋找附近搜尋框
            search_selectors = [
                "//input[@id='searchboxinput']",
                "//input[contains(@class, 'searchboxinput')]",
                "//input[contains(@class, 'xiQnY')]",
                "//input[@name='q']",
                "//input[@placeholder='搜尋附近地點']",
                "//input[contains(@placeholder, '附近')]",
                "//input[contains(@placeholder, 'nearby')]"
            ]
            
            nearby_search = None
            for selector in search_selectors:
                try:
                    nearby_search = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not nearby_search:
                print("找不到附近搜尋框")
                return False
            
            nearby_search.clear()
            nearby_search.send_keys(facility_name)
            nearby_search.send_keys(Keys.RETURN)
            
            # 等待搜尋結果載入
            time.sleep(5)
            print(f"附近設施搜尋完成: {facility_name}")
            return True
            
        except Exception as e:
            print(f"搜尋附近設施時發生錯誤: {e}")
            return False
    
    def direct_search_nearby(self, facility_name):
        """直接搜尋附近設施的備用方法"""
        try:
            search_box = self.driver.find_element(By.ID, "searchboxinput")
            search_box.clear()
            search_box.send_keys(f"{facility_name} 附近")
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"直接搜尋時發生錯誤: {e}")
            return False
    
    def extract_travel_time(self, element):
        """從元素中提取交通時間"""
        try:
            # 多種可能的時間格式
            time_patterns = [
                r'(\d+)\s*分鐘',
                r'(\d+)\s*min',
                r'(\d+)\s*分',
                r'(\d+)\s*m'
            ]
            
            # 在整個元素中搜尋時間資訊
            element_text = element.text
            
            for pattern in time_patterns:
                matches = re.findall(pattern, element_text, re.IGNORECASE)
                if matches:
                    minutes = int(matches[0])
                    return minutes, f"{minutes}分鐘"
            
            # 如果沒找到，嘗試在子元素中搜尋
            time_elements = element.find_elements(By.XPATH, ".//*[contains(text(), '分') or contains(text(), 'min')]")
            
            for time_elem in time_elements:
                time_text = time_elem.text
                for pattern in time_patterns:
                    match = re.search(pattern, time_text, re.IGNORECASE)
                    if match:
                        minutes = int(match.group(1))
                        return minutes, time_text
            
            return None, None
            
        except Exception as e:
            print(f"提取時間時發生錯誤: {e}")
            return None, None
    
    def get_facility_info(self, element):
        """獲取設施資訊"""
        try:
            # 多種可能的名稱選擇器
            name_selectors = [
                ".//div[@class='qBF1Pd fontHeadlineSmall']",
                ".//div[contains(@class, 'fontHeadlineSmall')]",
                ".//h3",
                ".//div[@class='fontHeadlineSmall']"
            ]
            
            facility_name = None
            for selector in name_selectors:
                try:
                    name_element = element.find_element(By.XPATH, selector)
                    facility_name = name_element.text.strip()
                    if facility_name:
                        break
                except NoSuchElementException:
                    continue
            
            if not facility_name:
                facility_name = "未知設施"
            
            # 獲取 W4Efsd div 的完整內容（包含分類標示）
            w4efsd_info = None
            try:
                w4efsd_element = element.find_element(By.XPATH, ".//div[@class='W4Efsd']")
                w4efsd_info = w4efsd_element.text.strip()
            except NoSuchElementException:
                w4efsd_info = "資訊未找到"
            
            # 嘗試從 W4Efsd 中提取地址（通常是最後一部分）
            address = None
            try:
                # 尋找地址相關的 span
                address_selectors = [
                    ".//div[@class='W4Efsd']//span[@class='mgr77e']",
                    ".//span[contains(@class, 'mgr77e')]",
                    ".//span[contains(text(), '台') or contains(text(), '市') or contains(text(), '區') or contains(text(), '路') or contains(text(), '街')]"
                ]
                
                for selector in address_selectors:
                    try:
                        address_element = element.find_element(By.XPATH, selector)
                        address = address_element.text.strip()
                        if address:
                            break
                    except NoSuchElementException:
                        continue
                
                # 如果沒找到專門的地址，嘗試從 W4Efsd 文字中提取
                if not address and w4efsd_info:
                    # 分割文字，通常地址在最後
                    parts = w4efsd_info.split('·')
                    for part in reversed(parts):
                        part = part.strip()
                        if any(keyword in part for keyword in ['台', '市', '區', '路', '街', '號']):
                            address = part
                            break
                
            except Exception:
                pass
            
            if not address:
                address = "地址未找到"
            
            return facility_name, address, w4efsd_info
            
        except Exception as e:
            print(f"獲取設施資訊時發生錯誤: {e}")
            return None, None, None
    
    def crawl_facilities(self, address, facility_type):
        """主要爬蟲函數"""
        print("開始爬蟲程序...")
        
        # 搜尋地址
        if not self.search_address(address):
            return False
        
        # 搜尋附近設施
        if not self.search_nearby_facilities(facility_type):
            return False
        
        # 等待結果載入
        time.sleep(5)
        
        try:
            # 多種可能的結果容器選擇器
            container_selectors = [
                "//div[@role='main']",
                "//div[contains(@class, 'siAUzd')]",
                "//div[@id='pane']"
            ]
            
            results_container = None
            for selector in container_selectors:
                try:
                    results_container = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not results_container:
                print("找不到結果容器")
                return False
            
            # 多種可能的結果項目選擇器
            item_selectors = [
                "//div[@class='Nv2PK THOPZb CpccDe ']",
                "//div[contains(@class, 'Nv2PK')]",
                "//div[@data-result-index]",
                "//div[contains(@class, 'THOPZb')]"
            ]
            
            result_items = []
            for selector in item_selectors:
                result_items = self.driver.find_elements(By.XPATH, selector)
                if result_items:
                    break
            
            if not result_items:
                print("找不到搜尋結果項目")
                return False
            
            print(f"找到 {len(result_items)} 個結果")
            
            for i, item in enumerate(result_items[:15]):  # 處理前15個結果
                try:
                    print(f"處理第 {i+1} 個結果...")
                    
                    # 獲取設施資訊（包含 W4Efsd 資訊）
                    facility_name, facility_address, w4efsd_info = self.get_facility_info(item)
                    
                    if facility_name and facility_name != "未知設施":
                        result = {
                            "設施名稱": facility_name,
                            "地址": facility_address,
                            "設施資訊": w4efsd_info,
                            "設施類型": facility_type,
                            "搜尋地址": address
                        }
                        self.results.append(result)
                        print(f"✓ 找到設施: {facility_name}")
                        print(f"   資訊: {w4efsd_info}")
                    else:
                        print(f"✗ 無法獲取設施資訊")
                    
                except Exception as e:
                    print(f"處理第 {i+1} 個結果時發生錯誤: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"爬取過程中發生錯誤: {e}")
            return False
    
    def save_results(self, filename="google_maps_results.json"):
        """儲存結果到 JSON 檔案"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n結果已儲存到 {filename}")
            print(f"共找到 {len(self.results)} 個設施")
            
            # 顯示結果摘要
            if self.results:
                print("\n=== 結果摘要 ===")
                for i, result in enumerate(self.results, 1):
                    print(f"{i}. {result['設施名稱']} - {result['地址']}")
                    print(f"   設施資訊: {result['設施資訊']}")
            
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
    address = "臺中市北區三民路三段"
    facility_type = "車站"
    
    print("=== Google Maps 爬蟲程式 ===")
    print(f"搜尋地址: {address}")
    print(f"設施類型: {facility_type}")
    print("=" * 40)
    
    # 創建爬蟲實例
    crawler = GoogleMapsCrawler(headless=False)
    
    try:
        # 執行爬蟲
        success = crawler.crawl_facilities(address, facility_type)
        
        if success:
            # 儲存結果
            filename = f"nearby_{facility_type}.json"
            crawler.save_results(filename)
        else:
            print("爬蟲執行失敗")
    
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        crawler.close()


if __name__ == "__main__":
    main()