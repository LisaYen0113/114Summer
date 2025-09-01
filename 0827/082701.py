from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, json

# 啟動瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://buy.yungching.com.tw/list/台北市-_c/?pg=1")

wait = WebDriverWait(driver, 10)

all_data = []
page = 1

while True:
    print(f"正在抓第 {page} 頁...")
    
    # 滾動到底確保 lazy load
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 抓取房屋卡片
    houses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.buy-item")))

    for h in houses:
        try:
            title = h.find_element(By.CSS_SELECTOR, ".caseName").text.strip()
            addr = h.find_element(By.CSS_SELECTOR, ".address").text if h.find_elements(By.CSS_SELECTOR, ".address") else ""
            case_type = h.find_element(By.CSS_SELECTOR, ".caseType").text if h.find_elements(By.CSS_SELECTOR, ".caseType") else ""
            reg_area = h.find_element(By.CSS_SELECTOR, ".regArea").text if h.find_elements(By.CSS_SELECTOR, ".regArea") else ""
            main_area = h.find_element(By.CSS_SELECTOR, ".mainArea").text if h.find_elements(By.CSS_SELECTOR, ".mainArea") else ""
            floor = h.find_element(By.CSS_SELECTOR, ".floor").text if h.find_elements(By.CSS_SELECTOR, ".floor") else ""
            room = h.find_element(By.CSS_SELECTOR, ".room").text if h.find_elements(By.CSS_SELECTOR, ".room") else ""
            price = h.find_element(By.CSS_SELECTOR, ".price").text if h.find_elements(By.CSS_SELECTOR, ".price") else ""
            origin_price = h.find_element(By.CSS_SELECTOR, ".origin-price").text if h.find_elements(By.CSS_SELECTOR, ".origin-price") else None
            discount = h.find_element(By.CSS_SELECTOR, ".discount").text if h.find_elements(By.CSS_SELECTOR, ".discount") else None
            note = h.find_element(By.CSS_SELECTOR, ".note").text if h.find_elements(By.CSS_SELECTOR, ".note") else ""
            tags = [t.text.strip() for t in h.find_elements(By.CSS_SELECTOR, ".tag-list li") if t.text.strip()]
            link = h.find_element(By.CSS_SELECTOR, "a.link").get_attribute("href")

            all_data.append({
                "title": title,
                "address": addr,
                "type": case_type,
                "reg_area": reg_area,
                "main_area": main_area,
                "floor": floor,
                "room": room,
                "price": price,
                "origin_price": origin_price,
                "discount": discount,
                "note": note,
                "tags": tags,
                "url": link
            })
        except Exception as e:
            print("error:", e)

    # 嘗試找到下一頁按鈕
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "a.page-next")
        if "disabled" in next_btn.get_attribute("class"):
            print("已到最後一頁")
            break
        else:
            next_btn.click()
            page += 1
            time.sleep(3)
    except:
        print("沒有下一頁，結束")
        break

# 存成 JSON
with open("yungching.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

driver.quit()
print(f"共抓到 {len(all_data)} 筆房屋資料，已存成 yungching.json ✅")
