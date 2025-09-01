#PTT 黑特政治版

import requests
from bs4 import BeautifulSoup
import csv
import time

from ckip_transformers.nlp import CkipWordSegmenter

    
headers = {'User-Agent': 'Mozilla/5.0'}
cookies = {'over18': '1'}

def get_articles_from_index(index_url):
    res = requests.get(index_url, headers=headers, cookies=cookies)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    titles = soup.find_all('div', class_='title')
    links = []
    for title in titles:
        a_tag = title.find('a')
        if a_tag:
            full_url = 'https://www.ptt.cc' + a_tag['href']
            links.append(full_url)
    return links, soup

def get_prev_page_url(soup):
    btns = soup.find_all('a', class_='btn wide')
    for btn in btns:
        if '上頁' in btn.text:
            return 'https://www.ptt.cc' + btn['href']
    return None

def crawl_article(article_url):
    res = requests.get(article_url, headers=headers, cookies=cookies)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    title_tag = soup.find('title')
    title = title_tag.text if title_tag else '無標題'

    main_content = soup.find(id='main-content')
    
    # ❗只移除文章頭資訊，不移除留言
    for tag in main_content.find_all(['div', 'span'], class_=['article-metaline', 'article-metaline-right']):
        tag.decompose()

    content = main_content.text.strip()

    pushes = soup.find_all('div', class_='push')
    comments = []
    for push in pushes:
        tag = push.find('span', class_=lambda x: x and 'push-tag' in x)
        user = push.find('span', class_=lambda x: x and 'push-userid' in x)
        msg = push.find('span', class_=lambda x: x and 'push-content' in x)
        if tag and user and msg:
            content_text = msg.text.lstrip(': ').strip()
            comments.append([tag.text.strip(), user.text.strip(), content_text])
    
    return title, content, comments


def save_to_csv(filename, articles):
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for art in articles:
            title, content, comments = art
            writer.writerow(['文章標題', title])
            writer.writerow(['文章內容'])
            writer.writerow([content])
            writer.writerow([])
            writer.writerow(['推文類型', '使用者', '留言內容'])
            writer.writerows(comments)
            writer.writerow([])
            writer.writerow(['-'*80])
            writer.writerow([])

def main(pages_to_crawl=3, output_csv='HatePolitics_MultiPages.csv'):
    base_url = 'https://www.ptt.cc/bbs/HatePolitics/index.html'
    crawled_urls = set()
    all_articles = []

    current_url = base_url
    for page in range(pages_to_crawl):
        print(f'爬第 {page+1} 頁：{current_url}')
        article_links, soup = get_articles_from_index(current_url)

        # 過濾重複文章
        new_links = [url for url in article_links if url not in crawled_urls]
        print(f'找到 {len(new_links)} 篇新文章')

        for url in new_links:
            print(f'爬文章：{url}')
            try:
                title, content, comments = crawl_article(url)
                all_articles.append((title, content, comments))
                crawled_urls.add(url)
                time.sleep(0.5)  # 請勿太快爬，避免被擋
            except Exception as e:
                print(f'爬文章錯誤: {e}')
        
        prev_url = get_prev_page_url(soup)
        if not prev_url:
            print('沒有上一頁了，結束爬取')
            break
        current_url = prev_url

    print(f'共爬取 {len(all_articles)} 篇文章，開始存檔...')
    save_to_csv(output_csv, all_articles)
    print(f'完成！存檔路徑：{output_csv}')

if __name__ == '__main__':
    # 你可以修改參數，設定要爬幾頁
    # --- PTT 爬蟲區段 ---
    # （這部分就是你原本的爬蟲程式，包含 main()）
    main(pages_to_crawl=1)

    # --- CKIP 斷詞區段 ---
   

    # 初始化斷詞器（第一次跑會下載模型，請保持網路）
    ws_driver = CkipWordSegmenter(model="bert-base")

    # 讀取剛剛產出的 CSV
    articles = []
    with open('HatePolitics_MultiPages.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        current_article = {'title': '', 'content': '', 'comments': []}
        mode = ''
        for row in reader:
            if not row:
                continue
            if row[0] == '文章標題':
                if current_article['title']:
                    articles.append(current_article)
                    current_article = {'title': '', 'content': '', 'comments': []}
                current_article['title'] = row[1]
                mode = ''
            elif row[0] == '文章內容':
                mode = 'content'
            elif row[0] == '推文類型':
                mode = 'comment'
            elif row[0].startswith('--------------------------------------------------------------------------------'):
                continue
            else:
                if mode == 'content':
                    current_article['content'] += row[0] + '\n'
                elif mode == 'comment' and len(row) == 3:
                    current_article['comments'].append(row[2])
        if current_article['title']:
            articles.append(current_article)

    # 開始斷詞
    def segment_texts(texts):
        return ws_driver(texts)

    with open('HatePolitics_segmented.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for article in articles:
            writer.writerow(['文章標題', article['title']])
            writer.writerow(['文章內容（斷詞）'])

            content_ws = segment_texts([article['content']])
            writer.writerow([' '.join(content_ws[0])])
            writer.writerow([])

            if article['comments']:
                writer.writerow(['留言斷詞'])
                segmented_comments = segment_texts(article['comments'])
                for comment, seg in zip(article['comments'], segmented_comments):
                    writer.writerow([comment, ' '.join(seg)])
                writer.writerow([])
            writer.writerow(['-' * 80])
            writer.writerow([])

    print("斷詞完成，結果已儲存為 HatePolitics_segmented.csv")


