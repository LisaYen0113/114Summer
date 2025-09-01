from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

class SimpleFacebookCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.options)
        
    def crawl_simple(self, group_url):
        """簡化版爬蟲，使用最基本的方法"""
        print("=== 簡化版Facebook爬蟲 ===")
        
        # 登入
        self.driver.get("https://www.facebook.com/login")
        input("請完成登入後按 Enter 繼續...")
        
        # 導航到社團
        print(f"導航到: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)
        
        # 滾動幾次
        for i in range(5):
            print(f"滾動 {i+1}/5...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        
        # 方法1: 使用您原本的方法
        print("\n=== 方法1: 原始方法 ===")
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        posts1 = soup.find_all("div", {"data-ad-preview": "message"})
        posts2 = soup.find_all("div", {"dir": "auto"})
        all_posts = posts1 + posts2
        
        texts = [p.get_text(separator="\n", strip=True) for p in all_posts if p.get_text(strip=True)]
        unique_texts = list(dict.fromkeys(texts))
        
        print(f"方法1找到 {len(unique_texts)} 個文字內容")
        for i, text in enumerate(unique_texts[:5]):
            if len(text) > 20:  # 只顯示較長的內容
                print(f"內容 {i+1}: {text[:150]}...")
        
        # 方法2: 查找所有包含文字的span和div
        print(f"\n=== 方法2: 查找所有文字內容 ===")
        
        # 查找所有可能包含貼文內容的元素
        text_elements = []
        
        # span元素
        spans = soup.find_all('span', string=True)
        for span in spans:
            text = span.get_text(strip=True)
            if text and len(text) > 30:  # 過濾太短的內容
                text_elements.append(text)
        
        # div元素
        divs = soup.find_all('div')
        for div in divs:
            # 只取直接文字內容，不包含子元素
            if div.string:
                text = div.string.strip()
                if text and len(text) > 30:
                    text_elements.append(text)
        
        # 去重並過濾
        unique_elements = []
        seen = set()
        
        for text in text_elements:
            # 簡單的去重邏輯
            text_hash = hash(text[:50])
            if text_hash not in seen and len(text) > 30:
                seen.add(text_hash)
                unique_elements.append(text)
        
        print(f"方法2找到 {len(unique_elements)} 個文字內容")
        for i, text in enumerate(unique_elements[:10]):
            print(f"內容 {i+1}: {text[:150]}...")
            print("-" * 50)
        
        # 方法3: 使用Selenium直接獲取文字
        print(f"\n=== 方法3: Selenium直接獲取 ===")
        
        try:
            # 嘗試不同的選擇器
            selectors = [
                'span[dir="auto"]',
                'div[dir="auto"]',
                '[data-ad-preview="message"]',
                'span:not(:empty)',
                'div:not(:empty)'
            ]
            
            all_selenium_texts = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"選擇器 '{selector}' 找到 {len(elements)} 個元素")
                    
                    for elem in elements:
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 30 and len(text) < 2000:
                                all_selenium_texts.append(text)
                        except:
                            pass
                except Exception as e:
                    print(f"選擇器 '{selector}' 錯誤: {e}")
            
            # 去重
            unique_selenium_texts = list(dict.fromkeys(all_selenium_texts))
            print(f"Selenium方法找到 {len(unique_selenium_texts)} 個文字內容")
            
            for i, text in enumerate(unique_selenium_texts[:10]):
                print(f"內容 {i+1}: {text[:150]}...")
                print("-" * 50)
                
        except Exception as e:
            print(f"Selenium方法錯誤: {e}")
        
        # 保存所有結果
        all_results = {
            'method1_count': len(unique_texts),
            'method1_texts': unique_texts[:10],
            'method2_count': len(unique_elements),
            'method2_texts': unique_elements[:10],
            'method3_count': len(unique_selenium_texts) if 'unique_selenium_texts' in locals() else 0,
            'method3_texts': unique_selenium_texts[:10] if 'unique_selenium_texts' in locals() else []
        }
        
        import json
        with open('tmp_rovodev_crawl_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果已保存到 tmp_rovodev_crawl_results.json")
        
        return all_results
    
    def close(self):
        self.driver.quit()

# 執行
if __name__ == "__main__":
    crawler = SimpleFacebookCrawler()
    try:
        group_url = "https://www.facebook.com/groups/1713612772170903"
        results = crawler.crawl_simple(group_url)
    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        crawler.close()