import urllib.parse
import requests
import re
import time

def search_via_startpage(query, max_results=10):
    """
    使用 Startpage 搜尋 ptt.cc 相關結果
    """
    results = []
    
    try:
        print(f"嘗試 Startpage 搜尋: {query}")
        
        search_query = f"{query} site:ptt.cc"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://www.startpage.com/sp/search?query={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 找出所有 PTT 連結並去重
            ptt_links = list(set(re.findall(r'https?://[^"\s]*ptt\.cc[^"\s]*', content)))
            
            for link in ptt_links[:max_results]:
                # 嘗試從連結中提取標題資訊
                title = "PTT文章"
                if "/M." in link:
                    # 從連結中提取文章ID作為標題
                    match = re.search(r'/M\.(\d+)\.A', link)
                    if match:
                        title = f"PTT文章 (ID: {match.group(1)})"
                elif "/bbs/" in link:
                    # 從連結中提取看板名稱
                    match = re.search(r'/bbs/([^/]+)', link)
                    if match:
                        title = f"PTT {match.group(1)} 板"
                
                results.append({
                    'title': title,
                    'url': link,
                    'source': 'Startpage'
                })
                print(f"Startpage 找到: {title} - {link}")
                time.sleep(0.5)
        else:
            print(f"Startpage 回傳狀態碼非200: {response.status_code}")
                
    except Exception as e:
        print(f"Startpage 搜尋錯誤: {e}")
    
    return results


if __name__ == "__main__":
    # 讓使用者輸入想搜尋的字
    keyword = input("請輸入想搜尋的關鍵字：")
    max_results = input("要抓幾筆結果（預設 10）：")
    
    try:
        max_results = int(max_results) if max_results else 10
    except ValueError:
        max_results = 10
    
    data = search_via_startpage(keyword, max_results)
    
    # 格式化輸出結果
    print("\n" + "="*60)
    print(f"搜尋關鍵字：{keyword}")
    print(f"找到 {len(data)} 個 PTT 相關連結")
    print("="*60)
    
    if data:
        for i, result in enumerate(data, 1):
            print(f"{i}. {result['title']}")
            print(f"   連結：{result['url']}")
            print(f"   來源：{result['source']}")
            print()
        
        # 保存結果到檔案
        filename = f"ptt_search_{keyword.replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"PTT 搜尋結果\n")
            f.write(f"關鍵字：{keyword}\n")
            f.write(f"搜尋時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            for i, result in enumerate(data, 1):
                f.write(f"{i}. {result['title']}\n")
                f.write(f"   連結：{result['url']}\n")
                f.write(f"   來源：{result['source']}\n\n")
        
        print(f"結果已保存到：{filename}")
    else:
        print("沒有找到相關的 PTT 連結")
        print("建議：")
        print("1. 嘗試不同的關鍵字")
        print("2. 直接到 PTT 網站搜尋")
        print(f"3. 手動搜尋：https://www.ptt.cc/bbs/search?q={urllib.parse.quote(keyword)}")
