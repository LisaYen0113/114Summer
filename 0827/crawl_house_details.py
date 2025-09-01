from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, json
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def crawl_house_details():
    # 讀取現有的房屋資料
    with open("yungching.json", "r", encoding="utf-8") as f:
        houses_data = json.load(f)
    
    print(f"共有 {len(houses_data)} 筆房屋資料需要爬取詳細資訊")
    
    # 啟動瀏覽器
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    
    updated_count = 0
    
    try:
        for i, house in enumerate(houses_data):
            if not house.get("url"):
                print(f"第 {i+1} 筆資料沒有 URL，跳過")
                continue
                
            print(f"正在處理第 {i+1}/{len(houses_data)} 筆: {house.get('title', 'Unknown')}")
            
            try:
                # 訪問房屋內頁
                driver.get(house["url"])
                time.sleep(2)
                
                # 初始化新欄位
                house["age"] = ""
                house["floor_detail"] = ""
                house["yc_certification"] = {
                    "text": "",
                    "images": []
                }
                
                # 抓取 age 資訊
                try:
                    age_element = driver.find_element(By.CSS_SELECTOR, ".age")
                    house["age"] = age_element.text.strip()
                    print(f"  - Age: {house['age']}")
                except NoSuchElementException:
                    print("  - Age: 未找到")
                
                # 抓取 floor 資訊
                try:
                    floor_element = driver.find_element(By.CSS_SELECTOR, ".floor")
                    house["floor_detail"] = floor_element.text.strip()
                    print(f"  - Floor: {house['floor_detail']}")
                except NoSuchElementException:
                    print("  - Floor: 未找到")
                
                # 抓取 yc-certification 資訊
                try:
                    cert_element = driver.find_element(By.CSS_SELECTOR, ".yc-certification")
                    house["yc_certification"]["text"] = cert_element.text.strip()
                    
                    # 抓取認證區域內的圖片
                    cert_images = cert_element.find_elements(By.TAG_NAME, "img")
                    for img in cert_images:
                        img_src = img.get_attribute("src")
                        img_alt = img.get_attribute("alt") or ""
                        if img_src:
                            house["yc_certification"]["images"].append({
                                "src": img_src,
                                "alt": img_alt
                            })
                    
                    print(f"  - Certification: {house['yc_certification']['text']}")
                    print(f"  - Certification Images: {len(house['yc_certification']['images'])} 張")
                    
                except NoSuchElementException:
                    print("  - YC Certification: 未找到")
                
                updated_count += 1
                
                # 每處理 10 筆就儲存一次，避免資料遺失
                if updated_count % 10 == 0:
                    with open("yungching_updated.json", "w", encoding="utf-8") as f:
                        json.dump(houses_data, f, ensure_ascii=False, indent=2)
                    print(f"已處理 {updated_count} 筆，暫存檔案已更新")
                
            except TimeoutException:
                print(f"  - 頁面載入超時，跳過此筆資料")
                continue
            except Exception as e:
                print(f"  - 處理時發生錯誤: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n使用者中斷程式執行")
    finally:
        # 儲存最終結果
        with open("yungching_updated.json", "w", encoding="utf-8") as f:
            json.dump(houses_data, f, ensure_ascii=False, indent=2)
        
        driver.quit()
        print(f"\n爬蟲完成！共處理了 {updated_count} 筆資料")
        print("結果已儲存至 yungching_updated.json")

if __name__ == "__main__":
    crawl_house_details()