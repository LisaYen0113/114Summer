from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime

class FacebookGroupCrawler:
    def __init__(self, headless=False):
        self.options = Options()
        if not headless:
            self.options.add_argument("--start-maximized")
        else:
            self.options.add_argument("--headless")
        
        # 添加一些反檢測選項
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        self.posts_data = []
        
    def login_facebook(self):
        """登入Facebook"""
        print("正在打開Facebook登入頁面...")
        self.driver.get("https://www.facebook.com/login")
        input("請完成登入後按 Enter 繼續...")
        
    def navigate_to_group(self, group_url):
        """導航到目標社團"""
        print(f"正在導航到社團: {group_url}")
        self.driver.get(group_url)
        time.sleep(5)
        
    def scroll_and_load_posts(self, max_scrolls=10):
        """滾動頁面並載入更多貼文"""
        print(f"開始滾動載入貼文，最多滾動 {max_scrolls} 次...")
        
        scroll_pause_time = 3
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for scroll_count in range(max_scrolls):
            print(f"第 {scroll_count + 1} 次滾動...")
            
            # 滾動到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # 檢查是否有新內容載入
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("沒有更多內容可載入")
                break
            last_height = new_height
            
    def extract_post_content(self, post_element):
        """提取單個貼文的完整內容"""
        try:
            # 直接獲取元素的所有文字內容
            text = post_element.get_text(separator='\n', strip=True)
            
            # 如果直接獲取的文字太短，嘗試其他方法
            if not text or len(text) < 20:
                # 嘗試多種方式找到貼文內容
                content_selectors = [
                    '[data-ad-preview="message"]',
                    '[dir="auto"]',
                    'span',
                    'div',
                    '.userContent',
                    '.text_exposed_root',
                    '[data-testid="post_message"]'
                ]
                
                content_parts = []
                
                for selector in content_selectors:
                    elements = post_element.select(selector)
                    for element in elements:
                        elem_text = element.get_text(strip=True)
                        if elem_text and len(elem_text) > 10 and elem_text not in content_parts:
                            content_parts.append(elem_text)
                
                # 合併內容並去重
                text = '\n'.join(content_parts)
            
            return text
            
        except Exception as e:
            print(f"提取貼文內容時發生錯誤: {e}")
            return ""
    
    def extract_comments(self, post_element):
        """提取貼文的留言"""
        comments = []
        try:
            # 嘗試點擊"查看更多留言"按鈕
            try:
                see_more_comments = post_element.find_element(By.XPATH, ".//span[contains(text(), '查看更多留言') or contains(text(), 'View more comments')]")
                if see_more_comments:
                    self.driver.execute_script("arguments[0].click();", see_more_comments)
                    time.sleep(2)
            except:
                pass
            
            # 提取留言
            comment_selectors = [
                '[role="article"]',
                '.UFIComment',
                '[data-testid="UFI2Comment/body"]'
            ]
            
            soup = BeautifulSoup(post_element.get_attribute('outerHTML'), 'html.parser')
            
            for selector in comment_selectors:
                comment_elements = soup.select(selector)
                for comment_elem in comment_elements:
                    comment_text = comment_elem.get_text(strip=True)
                    if comment_text and len(comment_text) > 10:  # 過濾太短的內容
                        comments.append(comment_text)
            
            # 去重
            comments = list(dict.fromkeys(comments))
            
        except Exception as e:
            print(f"提取留言時發生錯誤: {e}")
            
        return comments
    
    def extract_post_metadata(self, post_element):
        """提取貼文的元數據（作者、時間等）"""
        metadata = {}
        
        try:
            # 提取作者名稱
            author_selectors = [
                'strong a',
                '[data-hovercard-prefer-more-content-show="1"]',
                '.actor'
            ]
            
            soup = BeautifulSoup(post_element.get_attribute('outerHTML'), 'html.parser')
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    metadata['author'] = author_elem.get_text(strip=True)
                    break
            
            # 提取時間戳
            time_selectors = [
                'abbr',
                '[data-utime]',
                'time'
            ]
            
            for selector in time_selectors:
                time_elem = soup.select_one(selector)
                if time_elem:
                    metadata['timestamp'] = time_elem.get('title') or time_elem.get_text(strip=True)
                    break
                    
        except Exception as e:
            print(f"提取元數據時發生錯誤: {e}")
            
        return metadata
    
    def crawl_posts(self, group_url, max_scrolls=10, include_comments=True):
        """主要的爬蟲函數"""
        try:
            self.login_facebook()
            self.navigate_to_group(group_url)
            self.scroll_and_load_posts(max_scrolls)
            
            print("開始提取貼文內容...")
            
            # 獲取頁面HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尋找貼文容器 - 使用更廣泛的選擇器
            post_selectors = [
                '[role="article"]',
                '[data-pagelet="FeedUnit"]',
                '.userContentWrapper',
                '[data-testid="fbfeed_story"]',
                'div[data-ad-preview="message"]',
                'div[dir="auto"]'
            ]
            
            all_posts = []
            for selector in post_selectors:
                posts = soup.select(selector)
                print(f"選擇器 '{selector}' 找到 {len(posts)} 個元素")
                all_posts.extend(posts)
            
            # 如果上述選擇器都沒找到，使用更基本的方法
            if not all_posts:
                print("使用基本方法查找包含文字的div元素...")
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if text and len(text) > 50 and len(text) < 2000:
                        # 檢查是否包含有意義的內容
                        if any('\u4e00' <= char <= '\u9fff' for char in text) or any(char.isalpha() for char in text):
                            all_posts.append(div)
            
            print(f"總共找到 {len(all_posts)} 個可能的貼文元素")
            
            processed_posts = []
            
            for i, post in enumerate(all_posts):
                print(f"處理第 {i+1} 個貼文...")
                
                # 提取貼文內容
                content = self.extract_post_content(post)
                
                print(f"第 {i+1} 個元素內容長度: {len(content)}")
                if content:
                    print(f"內容預覽: {content[:100]}...")
                
                if content and len(content) > 20:  # 過濾太短的內容
                    post_data = {
                        'id': i + 1,
                        'content': content,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # 提取元數據
                    metadata = self.extract_post_metadata(post)
                    post_data.update(metadata)
                    
                    # 如果需要提取留言
                    if include_comments:
                        try:
                            # 重新找到對應的WebElement來提取留言
                            post_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="article"]')
                            if i < len(post_elements):
                                comments = self.extract_comments(post_elements[i])
                                post_data['comments'] = comments
                                post_data['comment_count'] = len(comments)
                        except Exception as e:
                            print(f"提取第 {i+1} 個貼文的留言時發生錯誤: {e}")
                            post_data['comments'] = []
                            post_data['comment_count'] = 0
                    
                    processed_posts.append(post_data)
            
            # 去重處理
            unique_posts = []
            seen_contents = set()
            
            for post in processed_posts:
                content_hash = hash(post['content'][:100])  # 使用前100字符作為去重依據
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    unique_posts.append(post)
            
            self.posts_data = unique_posts
            print(f"成功提取 {len(unique_posts)} 個獨特貼文")
            
            return unique_posts
            
        except Exception as e:
            print(f"爬蟲過程中發生錯誤: {e}")
            return []
    
    def save_to_file(self, filename="fb_group_posts.json"):
        """將結果保存到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.posts_data, f, ensure_ascii=False, indent=2)
            print(f"結果已保存到 {filename}")
        except Exception as e:
            print(f"保存文件時發生錯誤: {e}")
    
    def print_results(self, max_posts=5):
        """打印結果摘要"""
        print(f"\n=== 爬蟲結果摘要 ===")
        print(f"總共提取了 {len(self.posts_data)} 個貼文")
        
        for i, post in enumerate(self.posts_data[:max_posts]):
            print(f"\n--- 貼文 {i+1} ---")
            print(f"作者: {post.get('author', '未知')}")
            print(f"時間: {post.get('timestamp', '未知')}")
            print(f"內容: {post['content'][:200]}...")
            if 'comments' in post:
                print(f"留言數: {post.get('comment_count', 0)}")
                if post['comments']:
                    print("部分留言:")
                    for j, comment in enumerate(post['comments'][:3]):
                        print(f"  留言 {j+1}: {comment[:100]}...")
            print("-" * 50)
    
    def close(self):
        """關閉瀏覽器"""
        self.driver.quit()

# 使用範例
if __name__ == "__main__":
    # 創建爬蟲實例
    crawler = FacebookGroupCrawler(headless=False)
    
    try:
        # 目標社團URL
        group_url = "https://www.facebook.com/groups/1713612772170903"
        
        # 開始爬蟲
        posts = crawler.crawl_posts(
            group_url=group_url,
            max_scrolls=10,  # 滾動次數
            include_comments=True  # 是否包含留言
        )
        
        # 顯示結果
        crawler.print_results(max_posts=10)
        
        # 保存結果
        crawler.save_to_file("fb_group_posts.json")
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        crawler.close()