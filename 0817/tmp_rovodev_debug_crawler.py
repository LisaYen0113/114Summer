from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json

class FacebookDebugCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def debug_page_structure(self, group_url):
        """調試頁面結構，找出正確的選擇器"""
        print("=== Facebook 頁面結構調試 ===")
        
        # 登入
        self.driver.get("https://www.facebook.com/login")
        input("請完成登入後按 Enter 繼續...")
        
        # 導航到社團
        print(f"導航到: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)
        
        # 滾動一次載入更多內容
        print("滾動載入內容...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 獲取頁面HTML
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== 調試信息 ===")
        
        # 1. 檢查常見的貼文容器
        selectors_to_test = [
            ('[role="article"]', 'role="article"'),
            ('[data-pagelet="FeedUnit"]', 'data-pagelet="FeedUnit"'),
            ('.userContentWrapper', 'userContentWrapper class'),
            ('[data-testid="fbfeed_story"]', 'data-testid="fbfeed_story"'),
            ('div[data-ad-preview="message"]', 'data-ad-preview="message"'),
            ('div[dir="auto"]', 'dir="auto"'),
            ('[data-testid="post_message"]', 'data-testid="post_message"'),
            ('div[data-testid="story-body"]', 'data-testid="story-body"'),
            ('div[data-ft]', 'data-ft attribute'),
            ('.story_body_container', 'story_body_container class'),
            ('[data-testid="story-subtitle"]', 'data-testid="story-subtitle"')
        ]
        
        for selector, description in selectors_to_test:
            elements = soup.select(selector)
            print(f"{description}: 找到 {len(elements)} 個元素")
            
            if elements:
                # 顯示前幾個元素的內容預覽
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10:
                        print(f"  元素 {i+1} 內容預覽: {text[:100]}...")
        
        # 2. 查找包含文字內容的div
        print(f"\n=== 查找包含文字的div元素 ===")
        all_divs = soup.find_all('div')
        text_divs = []
        
        for div in all_divs:
            text = div.get_text(strip=True)
            if text and len(text) > 50 and len(text) < 1000:  # 合理長度的文字
                # 檢查是否包含中文或英文內容
                if any('\u4e00' <= char <= '\u9fff' for char in text) or any(char.isalpha() for char in text):
                    text_divs.append((div, text))
        
        print(f"找到 {len(text_divs)} 個包含文字內容的div")
        
        # 顯示前5個文字內容
        for i, (div, text) in enumerate(text_divs[:5]):
            print(f"\n文字內容 {i+1}:")
            print(f"內容: {text[:200]}...")
            
            # 顯示該div的屬性
            attrs = div.attrs
            if attrs:
                print(f"屬性: {attrs}")
        
        # 3. 保存完整HTML用於分析
        with open('tmp_rovodev_page_source.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n完整頁面HTML已保存到 tmp_rovodev_page_source.html")
        
        # 4. 嘗試使用Selenium直接查找元素
        print(f"\n=== 使用Selenium查找元素 ===")
        selenium_selectors = [
            (By.CSS_SELECTOR, '[role="article"]'),
            (By.CSS_SELECTOR, 'div[data-ad-preview="message"]'),
            (By.CSS_SELECTOR, 'div[dir="auto"]'),
            (By.XPATH, '//div[contains(@data-testid, "post")]'),
            (By.XPATH, '//div[contains(@data-testid, "story")]'),
            (By.CLASS_NAME, 'userContent'),
            (By.XPATH, '//span[contains(@dir, "auto")]'),
        ]
        
        for by_method, selector in selenium_selectors:
            try:
                elements = self.driver.find_elements(by_method, selector)
                print(f"Selenium {str(by_method)} '{selector}': 找到 {len(elements)} 個元素")
                
                if elements:
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 10:
                                print(f"  元素 {i+1}: {text[:100]}...")
                        except:
                            pass
            except Exception as e:
                print(f"Selenium {str(by_method)} '{selector}': 錯誤 - {e}")
    
    def close(self):
        self.driver.quit()

# 執行調試
if __name__ == "__main__":
    debugger = FacebookDebugCrawler()
    try:
        group_url = "https://www.facebook.com/groups/1713612772170903"
        debugger.debug_page_structure(group_url)
    except Exception as e:
        print(f"調試過程中發生錯誤: {e}")
    finally:
        debugger.close()