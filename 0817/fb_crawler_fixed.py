from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

class FacebookGroupCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.options)
        self.all_texts = []
        
    def login_and_navigate(self, target_url):
        """登入Facebook並導航到目標社團"""
        # 1. 登入 Facebook
        self.driver.get("https://www.facebook.com/login")
        input("請登入完成後按 Enter...")
        
        # 2. 打開目標社團
        self.driver.get(target_url)
        time.sleep(5)
    
    def scroll_and_extract_posts(self, scroll_count=10):
        """滾動並提取貼文 - 使用原本有效的方法"""
        scroll_pause_time = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        print(f"開始滾動並提取貼文，共 {scroll_count} 次...")
        
        for scroll_num in range(scroll_count):
            print(f"第 {scroll_num + 1} 次滾動...")
            
            # 取得目前頁面的 HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # 找出可能的貼文 - 使用您原本成功的方法
            posts1 = soup.find_all("div", {"data-ad-preview": "message"})
            posts2 = soup.find_all("div", {"dir": "auto"})
            all_posts = posts1 + posts2
            
            print(f"  data-ad-preview='message': {len(posts1)} 個")
            print(f"  dir='auto': {len(posts2)} 個")
            
            # 轉文字存起來 - 保持原本的邏輯
            texts = [p.get_text(separator="\\n", strip=True) for p in all_posts if p.get_text(strip=True)]
            self.all_texts.extend(texts)
            
            print(f"  本次提取到 {len(texts)} 個文字內容")
            
            # 滾動
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("  沒有更多內容可載入")
                break
            last_height = new_height
        
        # 去重 - 保持原本的邏輯
        self.all_texts_unique = list(dict.fromkeys(self.all_texts))
        print(f"\\n去重後共有 {len(self.all_texts_unique)} 個獨特內容")
        
        return self.all_texts_unique
    
    def extract_comments_for_posts(self):
        """為每個貼文提取留言"""
        print("\\n開始提取留言...")
        
        posts_with_comments = []
        
        # 重新獲取頁面HTML來分析留言
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # 找到所有可能的留言區域
        comment_selectors = [
            "div[role='article']",  # 留言通常在article role中
            "div[data-testid*='comment']",  # 包含comment的testid
            "span[dir='auto']",  # 留言文字通常也是dir=auto
        ]
        
        all_comments = []
        for selector in comment_selectors:
            comment_elements = soup.select(selector)
            for elem in comment_elements:
                comment_text = elem.get_text(strip=True)
                # 過濾：留言通常比貼文短，且不應該與已知貼文重複
                if (comment_text and 
                    10 < len(comment_text) < 500 and  # 合理的留言長度
                    comment_text not in self.all_texts_unique):  # 不是已知的貼文
                    all_comments.append(comment_text)
        
        # 去重留言
        unique_comments = list(dict.fromkeys(all_comments))
        print(f"提取到 {len(unique_comments)} 個可能的留言")
        
        # 嘗試將留言與貼文關聯（簡化版本）
        for i, post_content in enumerate(self.all_texts_unique):
            post_data = {
                'id': i + 1,
                'content': post_content,
                'extracted_at': datetime.now().isoformat(),
                'comments': [],
                'estimated_comments': []
            }
            
            # 簡單的留言關聯邏輯：找到可能相關的留言
            # 這裡使用啟發式方法，實際效果可能需要調整
            related_comments = []
            for comment in unique_comments[:20]:  # 限制檢查數量避免過慢
                # 如果留言很短且在貼文附近出現，可能是相關的
                if len(comment) < len(post_content) * 0.5:
                    related_comments.append(comment)
            
            post_data['estimated_comments'] = related_comments[:5]  # 最多5個估計相關的留言
            posts_with_comments.append(post_data)
        
        return posts_with_comments
    
    def save_results(self, posts_data, filename="fb_posts_and_comments.json"):
        """保存結果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, ensure_ascii=False, indent=2)
            print(f"結果已保存到 {filename}")
        except Exception as e:
            print(f"保存文件時發生錯誤: {e}")
    
    def print_results(self, posts_data, max_display=5):
        """顯示結果"""
        print(f"\\n=== 爬蟲結果 ===")
        print(f"共抓到 {len(posts_data)} 篇貼文")
        
        for i, post in enumerate(posts_data[:max_display]):
            print(f"\\n貼文 {i+1}：")
            print(f"{post['content']}")
            if post['estimated_comments']:
                print(f"可能的留言 ({len(post['estimated_comments'])} 個):")
                for j, comment in enumerate(post['estimated_comments'][:3]):
                    print(f"  留言 {j+1}: {comment}")
            print('-' * 40)
    
    def crawl(self, target_url, scroll_count=10):
        """主要爬蟲函數"""
        try:
            # 登入並導航
            self.login_and_navigate(target_url)
            
            # 提取貼文（使用原本有效的方法）
            posts_text = self.scroll_and_extract_posts(scroll_count)
            
            # 提取留言
            posts_with_comments = self.extract_comments_for_posts()
            
            # 顯示結果
            self.print_results(posts_with_comments)
            
            # 保存結果
            self.save_results(posts_with_comments)
            
            return posts_with_comments
            
        except Exception as e:
            print(f"爬蟲過程中發生錯誤: {e}")
            return []
    
    def close(self):
        """關閉瀏覽器"""
        self.driver.quit()

# 使用範例
if __name__ == "__main__":
    crawler = FacebookGroupCrawler()
    
    try:
        target_url = "https://www.facebook.com/groups/1713612772170903"
        
        # 開始爬蟲
        results = crawler.crawl(target_url, scroll_count=10)
        
        print(f"\\n爬蟲完成！共處理 {len(results)} 個貼文")
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        crawler.close()