import json
import requests
import re
import time
import os
from bs4 import BeautifulSoup
import urllib.parse

class PTTCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        })
        # PTT 需要設定 over18 cookie
        self.session.cookies.set('over18', '1', domain='.ptt.cc')
    
    def load_links_from_json(self, json_filename):
        """從 JSON 檔案讀取連結"""
        try:
            with open(json_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查是否為主檔案格式
            if 'all_links' in data:
                print(f"從主檔案 {json_filename} 讀取到 {data['total_unique_links']} 個連結")
                print(f"搜尋歷史: {len(data['search_history'])} 次搜尋")
                return data['all_links']
            else:
                # 舊格式
                print(f"從 {json_filename} 讀取到 {data['total_results']} 個連結")
                return data['links']
        except Exception as e:
            print(f"讀取 JSON 檔案錯誤: {e}")
            return []
    
    def load_links_from_txt(self, txt_filename):
        """從純連結文字檔讀取連結"""
        try:
            links = []
            with open(txt_filename, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url:
                        links.append({
                            'title': '未知標題',
                            'url': url,
                            'source': 'txt_file'
                        })
            print(f"從 {txt_filename} 讀取到 {len(links)} 個連結")
            return links
        except Exception as e:
            print(f"讀取文字檔案錯誤: {e}")
            return []
    
    def validate_ptt_url(self, url):
        """驗證 PTT 連結格式是否正確"""
        # 清理 URL
        clean_url = url.replace('\\', '').strip()
        
        # 檢查基本格式
        ptt_pattern = r'^https?://(?:www\.)?ptt\.cc/bbs/[^/]+/M\.\d+\.A\.[A-Z0-9]+\.html$'
        return re.match(ptt_pattern, clean_url) is not None, clean_url
    
    def crawl_ptt_article(self, url):
        """爬取單篇 PTT 文章"""
        try:
            # 驗證和清理 URL
            is_valid, clean_url = self.validate_ptt_url(url)
            if not is_valid:
                print(f"無效的 PTT 連結格式: {url}")
                return None
            
            print(f"正在爬取: {clean_url}")
            
            response = self.session.get(clean_url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"無法訪問文章，狀態碼: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章資訊
            article_data = {
                'url': clean_url,
                'original_url': url if url != clean_url else clean_url,
                'title': '',
                'author': '',
                'board': '',
                'date': '',
                'content': '',
                'comments': []
            }
            
            # 提取標題
            title_elem = soup.find('span', class_='article-meta-value')
            if title_elem:
                article_data['title'] = title_elem.get_text().strip()
            
            # 提取作者、看板、日期
            meta_spans = soup.find_all('span', class_='article-meta-value')
            if len(meta_spans) >= 4:
                article_data['author'] = meta_spans[0].get_text().strip()
                article_data['board'] = meta_spans[1].get_text().strip()
                article_data['title'] = meta_spans[2].get_text().strip()
                article_data['date'] = meta_spans[3].get_text().strip()
            
            # 先提取推文/留言（在移除之前）
            push_divs = soup.find_all('div', class_='push')
            for push_div in push_divs:
                push_tag = push_div.find('span', class_='push-tag')
                push_userid = push_div.find('span', class_='push-userid')
                push_content = push_div.find('span', class_='push-content')
                push_ipdatetime = push_div.find('span', class_='push-ipdatetime')
                
                if push_tag and push_userid and push_content:
                    comment = {
                        'type': push_tag.get_text().strip(),
                        'user': push_userid.get_text().strip(),
                        'content': push_content.get_text().strip(),
                        'datetime': push_ipdatetime.get_text().strip() if push_ipdatetime else ''
                    }
                    article_data['comments'].append(comment)
            
            # 提取文章內容（在提取推文後再移除推文區域）
            main_content = soup.find('div', id='main-content')
            if main_content:
                # 移除推文區域
                for push_div in main_content.find_all('div', class_='push'):
                    push_div.decompose()
                
                # 移除其他不需要的元素
                for elem in main_content.find_all(['span', 'div'], class_=['article-meta-tag', 'article-meta-value']):
                    elem.decompose()
                
                article_data['content'] = main_content.get_text().strip()
            
            print(f"成功爬取文章: {article_data['title']}")
            print(f"  作者: {article_data['author']}")
            print(f"  看板: {article_data['board']}")
            print(f"  留言數: {len(article_data['comments'])}")
            
            return article_data
            
        except Exception as e:
            print(f"爬取文章錯誤 {url}: {e}")
            return None
    
    def crawl_all_articles(self, links, output_filename=None, delay=1):
        """爬取所有文章"""
        all_articles = []
        invalid_links = 0
        failed_crawls = 0
        
        for i, link_info in enumerate(links, 1):
            url = link_info['url']
            print(f"\n進度: {i}/{len(links)}")
            
            article_data = self.crawl_ptt_article(url)
            if article_data:
                all_articles.append(article_data)
            else:
                # 檢查是否為無效連結格式
                is_valid, _ = self.validate_ptt_url(url)
                if not is_valid:
                    invalid_links += 1
                else:
                    failed_crawls += 1
            
            # 延遲避免被封鎖
            if i < len(links):
                print(f"等待 {delay} 秒...")
                time.sleep(delay)
        
        # 顯示統計資訊
        print(f"\n爬取統計:")
        print(f"  總連結數: {len(links)}")
        print(f"  成功爬取: {len(all_articles)}")
        print(f"  無效連結: {invalid_links}")
        print(f"  爬取失敗: {failed_crawls}")
        
        # 保存結果
        if output_filename:
            self.save_articles(all_articles, output_filename)
        
        return all_articles
    
    def save_articles(self, articles, base_filename):
        """保存爬取的文章資料，每次產生新的檔案"""
        try:
            # 產生帶時間戳記的檔案名稱
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            json_filename = f"{base_filename}_{timestamp}.json"
            txt_filename = f"{base_filename}_{timestamp}.txt"
            
            output_data = {
                'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_articles': len(articles),
                'successful_crawls': len([a for a in articles if a]),
                'articles': articles
            }
            
            # 保存為 JSON 格式
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            # 保存為可讀的文字格式
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"PTT 文章爬取結果\n")
                f.write(f"爬取時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"總文章數: {len(articles)}\n")
                f.write(f"成功爬取: {len([a for a in articles if a])} 篇\n")
                f.write("="*80 + "\n\n")
                
                for i, article in enumerate(articles, 1):
                    if article:  # 只處理成功爬取的文章
                        f.write(f"文章 {i}: {article['title']}\n")
                        f.write(f"作者: {article['author']}\n")
                        f.write(f"看板: {article['board']}\n")
                        f.write(f"日期: {article['date']}\n")
                        f.write(f"網址: {article['url']}\n")
                        
                        # 如果有找到關鍵字資訊，也顯示
                        if 'found_by_keyword' in article:
                            f.write(f"搜尋關鍵字: {article['found_by_keyword']}\n")
                        
                        f.write("-" * 40 + "\n")
                        f.write("內容:\n")
                        content_preview = article['content'][:500] + "..." if len(article['content']) > 500 else article['content']
                        f.write(content_preview)
                        f.write(f"\n\n留言數: {len(article['comments'])}\n")
                        
                        if article['comments']:
                            f.write("前5則留言:\n")
                            for comment in article['comments'][:5]:
                                f.write(f"  {comment['type']} {comment['user']}: {comment['content']}\n")
                        
                        f.write("\n" + "="*80 + "\n\n")
            
            print(f"\n爬取結果已保存:")
            print(f"  JSON格式: {json_filename}")
            print(f"  文字格式: {txt_filename}")
            
        except Exception as e:
            print(f"保存文章錯誤: {e}")


def main():
    crawler = PTTCrawler()
    
    print("PTT 文章爬蟲程式")
    print("="*50)
    
    # 檢查是否有主檔案
    master_file = "ptt_links_master.json"
    other_json_files = [f for f in os.listdir('.') if f.startswith('ptt_links_') and f.endswith('.json') and f != master_file]
    txt_files = [f for f in os.listdir('.') if f.startswith('ptt_urls_') and f.endswith('.txt')]
    
    all_files = []
    
    # 優先顯示主檔案
    if os.path.exists(master_file):
        print("找到主要連結檔案:")
        print(f"  1. {master_file} (推薦 - 包含所有累積的連結)")
        all_files.append(('json', master_file))
    
    # 顯示其他檔案
    if other_json_files or txt_files:
        print("\n其他連結檔案:")
        
        if other_json_files:
            print("  JSON 格式:")
            for f in other_json_files:
                print(f"    {len(all_files) + 1}. {f}")
                all_files.append(('json', f))
        
        if txt_files:
            print("  純連結格式:")
            for f in txt_files:
                print(f"    {len(all_files) + 1}. {f}")
                all_files.append(('txt', f))
    
    if not all_files:
        print("找不到連結檔案！")
        print("請先執行搜尋程式 (0808.py) 產生連結檔案")
        return
    
    # 讓使用者選擇檔案
    try:
        choice = int(input(f"\n請選擇要爬取的檔案 (1-{len(all_files)}): ")) - 1
        if choice < 0 or choice >= len(all_files):
            print("選擇無效！")
            return
        
        file_type, filename = all_files[choice]
        
        # 讀取連結
        if file_type == 'json':
            links = crawler.load_links_from_json(filename)
        else:
            links = crawler.load_links_from_txt(filename)
        
        if not links:
            print("沒有找到有效的連結！")
            return
        
        # 設定延遲時間
        delay = input("設定爬取延遲秒數 (預設 1 秒，避免被封鎖): ")
        try:
            delay = float(delay) if delay else 1.0
        except ValueError:
            delay = 1.0
        
        # 開始爬取
        if filename == "ptt_links_master.json":
            output_name = "ptt_articles_master"
        else:
            output_name = filename.replace('ptt_links_', 'ptt_articles_').replace('ptt_urls_', 'ptt_articles_').replace('.json', '').replace('.txt', '')
        
        print(f"\n開始爬取 {len(links)} 篇文章...")
        print(f"延遲設定: {delay} 秒")
        print(f"輸出檔案將以 '{output_name}_時間戳記' 格式命名")
        print("注意: 爬取過程可能需要較長時間，請耐心等待...")
        
        articles = crawler.crawl_all_articles(links, output_name, delay)
        
        print(f"\n爬取完成！成功爬取 {len(articles)} 篇文章")
        
    except KeyboardInterrupt:
        print("\n\n使用者中斷爬取")
    except ValueError:
        print("輸入無效！")
    except Exception as e:
        print(f"執行錯誤: {e}")


if __name__ == "__main__":
    main()