import requests
from bs4 import BeautifulSoup
import json
import time
import re

headers = {'User-Agent': 'Mozilla/5.0'}
cookies = {'over18': '1'}

def extract_area_keyword(found_by_keyword):
    """從found_by_keyword中提取地區和關鍵詞"""
    parts = found_by_keyword.split()
    if len(parts) >= 2:
        area = parts[0]
        keyword = parts[1]
    else:
        area = found_by_keyword
        keyword = ""
    return area, keyword

def crawl_ptt_article(article_url):
    """爬取PTT文章內容"""
    try:
        res = requests.get(article_url, headers=headers, cookies=cookies)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 獲取標題
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else '無標題'
        # 清理標題格式
        title = re.sub(r'^\[.*?\]\s*', '', title)  # 移除開頭的[板名]
        title = re.sub(r'\s*-\s*PTT.*$', '', title)  # 移除結尾的PTT資訊

        # 先獲取推文（在移除之前）
        pushes = soup.find_all('div', class_='push')
        comments = []
        for push in pushes:
            tag_elem = push.find('span', class_=lambda x: x and 'push-tag' in x)
            user_elem = push.find('span', class_=lambda x: x and 'push-userid' in x)
            msg_elem = push.find('span', class_=lambda x: x and 'push-content' in x)
            
            if tag_elem and user_elem and msg_elem:
                tag = tag_elem.text.strip()
                user = user_elem.text.strip()
                text = msg_elem.text.lstrip(': ').strip()
                
                comments.append({
                    "user": user,
                    "tag": tag,
                    "text": text
                })

        # 獲取文章內容
        main_content = soup.find(id='main-content')
        if not main_content:
            return None, None, []

        # 移除文章頭資訊
        for tag in main_content.find_all(['div', 'span'], class_=['article-metaline', 'article-metaline-right']):
            tag.decompose()

        # 移除推文部分，只保留文章正文
        for tag in main_content.find_all('div', class_='push'):
            tag.decompose()

        content = main_content.get_text().strip()
        
        # 清理內容
        content = re.sub(r'\n\s*\n', '\n', content)  # 移除多餘空行
        content = re.sub(r'--\n.*', '', content, flags=re.DOTALL)  # 移除簽名檔

        return title, content, comments

    except Exception as e:
        print(f"爬取文章錯誤 {article_url}: {e}")
        return None, None, []

def main():
    # 讀取link.json
    try:
        with open('link.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            links_data = data.get('all_links', [])
    except Exception as e:
        print(f"讀取link.json錯誤: {e}")
        return

    print(f"共找到 {len(links_data)} 個連結")
    
    results = []
    
    for i, link_info in enumerate(links_data):
        url = link_info.get('url', '')
        found_by_keyword = link_info.get('found_by_keyword', '')
        
        print(f"正在處理第 {i+1}/{len(links_data)} 個連結: {url}")
        
        # 提取地區和關鍵詞
        area, keyword = extract_area_keyword(found_by_keyword)
        
        # 爬取文章
        title, content, comments = crawl_ptt_article(url)
        
        if title and content:
            result = {
                "area": area,
                "keyword": keyword,
                "url": url,
                "title": title,
                "content": content,
                "comments": comments
            }
            results.append(result)
            print(f"成功爬取: {title[:30]}...")
        else:
            print(f"爬取失敗: {url}")
        
        # 避免請求過快
        time.sleep(1)
        
        # 每10篇保存一次，避免資料遺失
        if (i + 1) % 10 == 0:
            with open('crawled_articles_temp.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"已保存臨時檔案，當前進度: {i+1}/{len(links_data)}")

    # 保存最終結果
    with open('crawled_articles.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"爬取完成！共成功爬取 {len(results)} 篇文章")
    print("結果已保存到 crawled_articles.json")

if __name__ == '__main__':
    main()