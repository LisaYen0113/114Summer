import urllib.parse
import requests
import re
import time
import json
import os

def save_to_master_json(new_data, keyword, filename):
    """
    將新的搜尋結果累積到主要 JSON 檔案中，並去重
    """
    try:
        # 嘗試讀取現有的檔案
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        else:
            # 如果檔案不存在，創建新的結構
            master_data = {
                "created_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "last_updated": "",
                "search_history": [],
                "total_unique_links": 0,
                "all_links": []
            }
        
        # 更新最後修改時間
        master_data["last_updated"] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 記錄這次搜尋
        search_record = {
            "keyword": keyword,
            "search_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "new_links_found": len(new_data)
        }
        master_data["search_history"].append(search_record)
        
        # 取得現有連結的 URL 集合（用於去重）
        existing_urls = {link["url"] for link in master_data["all_links"]}
        
        # 添加新連結（去重）
        new_links_added = 0
        for link in new_data:
            if link["url"] not in existing_urls:
                # 添加搜尋關鍵字資訊
                link_with_keyword = link.copy()
                link_with_keyword["found_by_keyword"] = keyword
                link_with_keyword["found_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                master_data["all_links"].append(link_with_keyword)
                existing_urls.add(link["url"])
                new_links_added += 1
        
        # 更新統計
        master_data["total_unique_links"] = len(master_data["all_links"])
        search_record["new_unique_links_added"] = new_links_added
        
        # 保存檔案
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"  本次新增 {new_links_added} 個不重複連結")
        print(f"  累積總連結數：{master_data['total_unique_links']}")
        
    except Exception as e:
        print(f"保存到主檔案錯誤: {e}")


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
            # 更精確的正則表達式，避免抓到 HTML 標籤
            ptt_pattern = r'https?://(?:www\.)?ptt\.cc/bbs/[^/]+/M\.\d+\.A\.[A-Z0-9]+\.html'
            ptt_links_raw = re.findall(ptt_pattern, content)
            
            # 清理連結，移除可能的 HTML 標籤和特殊字符
            ptt_links = []
            for link in ptt_links_raw:
                # 移除可能的反斜線和其他特殊字符
                clean_link = link.replace('\\', '').strip()
                # 確保連結格式正確
                if clean_link.startswith('http') and 'ptt.cc/bbs/' in clean_link and clean_link.endswith('.html'):
                    ptt_links.append(clean_link)
            
            # 去重
            ptt_links = list(set(ptt_links))
            
            for link in ptt_links[:max_results]:
                # 從連結中提取標題資訊
                title = "PTT文章"
                board_name = "未知看板"
                article_id = "未知ID"
                
                # 提取看板名稱
                board_match = re.search(r'/bbs/([^/]+)/', link)
                if board_match:
                    board_name = board_match.group(1)
                
                # 提取文章ID
                id_match = re.search(r'/M\.(\d+)\.A\.([A-Z0-9]+)\.html', link)
                if id_match:
                    article_id = id_match.group(1)
                    title = f"PTT {board_name} 板 - 文章ID: {article_id}"
                else:
                    title = f"PTT {board_name} 板"
                
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
        # 1. 保存詳細結果到文字檔
        txt_filename = f"ptt_search_{keyword.replace(' ', '_')}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"PTT 搜尋結果\n")
            f.write(f"關鍵字：{keyword}\n")
            f.write(f"搜尋時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            for i, result in enumerate(data, 1):
                f.write(f"{i}. {result['title']}\n")
                f.write(f"   連結：{result['url']}\n")
                f.write(f"   來源：{result['source']}\n\n")
        
        # 2. 累積保存到主要 JSON 檔案（去重功能）
        master_json_filename = "ptt_links_master.json"
        save_to_master_json(data, keyword, master_json_filename)
        
        # 3. 保存純連結列表（最簡潔的格式）
        links_filename = f"ptt_urls_{keyword.replace(' ', '_')}.txt"
        with open(links_filename, 'w', encoding='utf-8') as f:
            for result in data:
                f.write(f"{result['url']}\n")
        
        print(f"結果已保存到：")
        print(f"  詳細結果：{txt_filename}")
        print(f"  累積JSON：{master_json_filename}")
        print(f"  純連結：{links_filename}")
    else:
        print("沒有找到相關的 PTT 連結")
        print("建議：")
        print("1. 嘗試不同的關鍵字")
        print("2. 直接到 PTT 網站搜尋")
        print(f"3. 手動搜尋：https://www.ptt.cc/bbs/search?q={urllib.parse.quote(keyword)}")
