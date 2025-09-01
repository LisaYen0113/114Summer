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


def read_keywords_from_file(filename):
    """
    從文字檔案中讀取關鍵字列表
    每行一個關鍵字，忽略空行和以#開頭的註解行
    """
    keywords = []
    try:
        if not os.path.exists(filename):
            print(f"關鍵字檔案 {filename} 不存在")
            return keywords
            
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 忽略空行和註解行
                if line and not line.startswith('#'):
                    keywords.append(line)
                    print(f"讀取關鍵字 {line_num}: {line}")
        
        print(f"成功讀取 {len(keywords)} 個關鍵字")
        return keywords
        
    except Exception as e:
        print(f"讀取關鍵字檔案錯誤: {e}")
        return keywords

def batch_search_from_file(keywords_file, max_results=10, delay_between_searches=2):
    """
    從檔案讀取關鍵字並進行批量搜索
    """
    keywords = read_keywords_from_file(keywords_file)
    
    if not keywords:
        print("沒有找到有效的關鍵字")
        return
    
    print(f"\n開始批量搜索，共 {len(keywords)} 個關鍵字")
    print(f"每次搜索間隔 {delay_between_searches} 秒")
    print("="*60)
    
    total_results = 0
    successful_searches = 0
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] 搜索關鍵字: {keyword}")
        print("-" * 40)
        
        try:
            # 執行搜索
            results = search_via_multiple_engines(keyword, max_results)
            
            if results:
                successful_searches += 1
                total_results += len(results)
                
                # 保存個別搜索結果
                save_individual_results(results, keyword)
                
                # 累積到主檔案
                master_json_filename = "ptt_links_master.json"
                save_to_master_json(results, keyword, master_json_filename)
                
                print(f"✓ 找到 {len(results)} 個結果")
            else:
                print("✗ 沒有找到結果")
            
            # 搜索間隔（最後一次搜索不需要等待）
            if i < len(keywords):
                print(f"等待 {delay_between_searches} 秒後繼續...")
                time.sleep(delay_between_searches)
                
        except Exception as e:
            print(f"✗ 搜索失敗: {e}")
    
    # 顯示批量搜索總結
    print("\n" + "="*60)
    print("批量搜索完成！")
    print(f"成功搜索: {successful_searches}/{len(keywords)} 個關鍵字")
    print(f"總共找到: {total_results} 個結果")
    print(f"結果已累積保存到: ptt_links_master.json")
    print("="*60)

def save_individual_results(results, keyword):
    """
    保存個別關鍵字的搜索結果
    """
    if not results:
        return
        
    # 保存詳細結果到文字檔
    txt_filename = f"ptt_search_{keyword.replace(' ', '_').replace('/', '_')}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(f"PTT 搜尋結果\n")
        f.write(f"關鍵字：{keyword}\n")
        f.write(f"搜尋時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. {result['title']}\n")
            f.write(f"   連結：{result['url']}\n")
            f.write(f"   來源：{result['source']}\n\n")
    
    # 保存純連結列表
    links_filename = f"ptt_urls_{keyword.replace(' ', '_').replace('/', '_')}.txt"
    with open(links_filename, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"{result['url']}\n")

def search_via_multiple_engines(query, max_results=10):
    """
    使用多個搜索引擎搜尋 PTT 相關結果
    當一個引擎被封鎖時自動切換到其他引擎
    """
    results = []
    
    # 限制最大結果數
    if max_results > 20:
        print(f"⚠️  將最大結果數從 {max_results} 調整為 20（避免被封鎖）")
        max_results = 20
    
    print(f"🔍 搜尋關鍵字: {query} (最多 {max_results} 筆)")
    
    # 嘗試多個搜索引擎
    search_engines = [
        ("DuckDuckGo", search_via_duckduckgo),
        ("Bing", search_via_bing),
        ("Startpage", search_via_startpage_original)
    ]
    
    for engine_name, search_func in search_engines:
        print(f"\n🔄 嘗試使用 {engine_name} 搜索...")
        try:
            engine_results = search_func(query, max_results)
            if engine_results:
                results.extend(engine_results)
                print(f"✅ {engine_name} 找到 {len(engine_results)} 個結果")
                break  # 找到結果就停止嘗試其他引擎
            else:
                print(f"⚠️  {engine_name} 沒有找到結果")
        except Exception as e:
            print(f"❌ {engine_name} 搜索失敗: {e}")
    
    # 去重並限制結果數量
    unique_results = []
    seen_urls = set()
    
    for result in results:
        if result['url'] not in seen_urls and len(unique_results) < max_results:
            unique_results.append(result)
            seen_urls.add(result['url'])
    
    print(f"🎯 完成搜尋，共找到 {len(unique_results)} 個不重複結果")
    return unique_results

def search_via_duckduckgo(query, max_results=10):
    """使用 DuckDuckGo 搜索"""
    results = []
    
    try:
        search_query = f"{query} site:ptt.cc"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        session = requests.Session()
        session.trust_env = False
        
        response = session.get(url, headers=headers, timeout=15, proxies={})
        
        if response.status_code == 200:
            content = response.text
            
            # 找出PTT連結
            ptt_pattern = r'https?://(?:www\.)?ptt\.cc/bbs/[^/]+/M\.\d+\.A\.[A-Z0-9]+\.html'
            ptt_links = list(set(re.findall(ptt_pattern, content)))
            
            for i, link in enumerate(ptt_links[:max_results]):
                # 提取看板和文章資訊
                board_name = "未知看板"
                article_id = "未知ID"
                
                board_match = re.search(r'/bbs/([^/]+)/', link)
                if board_match:
                    board_name = board_match.group(1)
                
                id_match = re.search(r'/M\.(\d+)\.A\.([A-Z0-9]+)\.html', link)
                if id_match:
                    article_id = id_match.group(1)
                    title = f"PTT {board_name} 板 - 文章ID: {article_id}"
                else:
                    title = f"PTT {board_name} 板"
                
                results.append({
                    'title': title,
                    'url': link,
                    'source': 'DuckDuckGo',
                    'board': board_name,
                    'article_id': article_id
                })
                
                print(f"✓ [{i+1:2d}] {board_name} - {article_id}")
                
    except Exception as e:
        print(f"DuckDuckGo 搜索錯誤: {e}")
    
    return results

def search_via_bing(query, max_results=10):
    """使用 Bing 搜索"""
    results = []
    
    try:
        search_query = f"{query} site:ptt.cc"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        session = requests.Session()
        session.trust_env = False
        
        response = session.get(url, headers=headers, timeout=15, proxies={})
        
        if response.status_code == 200:
            content = response.text
            
            # 找出PTT連結
            ptt_pattern = r'https?://(?:www\.)?ptt\.cc/bbs/[^/]+/M\.\d+\.A\.[A-Z0-9]+\.html'
            ptt_links = list(set(re.findall(ptt_pattern, content)))
            
            for i, link in enumerate(ptt_links[:max_results]):
                # 提取看板和文章資訊
                board_name = "未知看板"
                article_id = "未知ID"
                
                board_match = re.search(r'/bbs/([^/]+)/', link)
                if board_match:
                    board_name = board_match.group(1)
                
                id_match = re.search(r'/M\.(\d+)\.A\.([A-Z0-9]+)\.html', link)
                if id_match:
                    article_id = id_match.group(1)
                    title = f"PTT {board_name} 板 - 文章ID: {article_id}"
                else:
                    title = f"PTT {board_name} 板"
                
                results.append({
                    'title': title,
                    'url': link,
                    'source': 'Bing',
                    'board': board_name,
                    'article_id': article_id
                })
                
                print(f"✓ [{i+1:2d}] {board_name} - {article_id}")
                
    except Exception as e:
        print(f"Bing 搜索錯誤: {e}")
    
    return results

def search_via_startpage_original(query, max_results=10):
    """
    使用 Startpage 搜尋 ptt.cc 相關結果
    改進版：添加更好的限制和錯誤處理
    """
    results = []
    
    # 限制最大結果數，避免請求過多
    if max_results > 20:
        print(f"⚠️  將最大結果數從 {max_results} 調整為 20（避免被封鎖）")
        max_results = 20
    
    try:
        print(f"🔍 搜尋關鍵字: {query} (最多 {max_results} 筆)")
        
        search_query = f"{query} site:ptt.cc"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://www.startpage.com/sp/search?query={encoded_query}"
        print(f"🌐 請求URL: {url}")
        
        # 檢查網路連線
        try:
            test_response = requests.get("https://www.google.com", timeout=5)
            print(f"✅ 網路連線正常 (Google回應: {test_response.status_code})")
        except Exception as e:
            print(f"❌ 網路連線測試失敗: {e}")
            print("請檢查網路連線或代理設定")
            return results
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 添加重試機制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 第 {attempt + 1} 次嘗試連接 Startpage...")
                
                # 清除可能的代理設定
                session = requests.Session()
                session.trust_env = False  # 忽略環境變數中的代理設定
                
                response = session.get(url, headers=headers, timeout=15, proxies={})
                
                if response.status_code == 200:
                    content = response.text
                    
                    # 檢查是否被封鎖或限制
                    if "blocked" in content.lower() or "captcha" in content.lower():
                        print("⚠️  可能遇到反爬蟲機制，請稍後再試")
                        return results
                    
                    # 找出所有 PTT 連結
                    ptt_pattern = r'https?://(?:www\.)?ptt\.cc/bbs/[^/]+/M\.\d+\.A\.[A-Z0-9]+\.html'
                    ptt_links_raw = re.findall(ptt_pattern, content)
                    
                    if not ptt_links_raw:
                        print(f"📝 第 {attempt + 1} 次嘗試：未找到PTT連結")
                        if attempt < max_retries - 1:
                            print(f"⏳ 等待 {(attempt + 1) * 2} 秒後重試...")
                            time.sleep((attempt + 1) * 2)
                            continue
                        else:
                            print("❌ 多次嘗試後仍未找到結果")
                            return results
                    
                    # 清理和去重連結
                    ptt_links = []
                    for link in ptt_links_raw:
                        clean_link = link.replace('\\', '').strip()
                        if (clean_link.startswith('http') and 
                            'ptt.cc/bbs/' in clean_link and 
                            clean_link.endswith('.html') and
                            clean_link not in [r['url'] for r in results]):
                            ptt_links.append(clean_link)
                    
                    # 去重
                    ptt_links = list(set(ptt_links))
                    
                    print(f"📊 找到 {len(ptt_links)} 個不重複連結")
                    
                    # 處理結果，限制數量
                    processed_count = 0
                    for link in ptt_links:
                        if processed_count >= max_results:
                            break
                            
                        # 從連結中提取資訊
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
                            'source': 'Startpage',
                            'board': board_name,
                            'article_id': article_id
                        })
                        
                        processed_count += 1
                        print(f"✓ [{processed_count:2d}] {board_name} - {article_id}")
                        
                        # 短暫延遲，避免請求過快
                        time.sleep(0.3)
                    
                    break  # 成功找到結果，跳出重試循環
                    
                elif response.status_code == 429:
                    print(f"⚠️  請求過於頻繁 (429)，等待 {(attempt + 1) * 5} 秒後重試...")
                    time.sleep((attempt + 1) * 5)
                    
                else:
                    print(f"❌ HTTP錯誤 {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    
            except requests.exceptions.Timeout:
                print(f"⏰ 請求超時，第 {attempt + 1} 次嘗試")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    
            except requests.exceptions.RequestException as e:
                print(f"🌐 網路錯誤: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
    except Exception as e:
        print(f"❌ 搜尋錯誤: {e}")
    
    print(f"🎯 完成搜尋，共找到 {len(results)} 個結果")
    return results


if __name__ == "__main__":
    print("PTT 搜索工具")
    print("="*40)
    print("1. 單次搜索")
    print("2. 批量搜索（從檔案讀取關鍵字）")
    print("="*40)
    
    mode = input("請選擇模式 (1/2)：").strip()
    
    if mode == "2":
        # 批量搜索模式
        keywords_file = input("請輸入關鍵字檔案名稱（預設：keywords.txt）：").strip()
        if not keywords_file:
            keywords_file = "keywords.txt"
        
        max_results = input("每個關鍵字要抓幾筆結果（預設 10）：").strip()
        try:
            max_results = int(max_results) if max_results else 10
        except ValueError:
            max_results = 10
        
        delay = input("搜索間隔秒數（預設 5 秒，建議不少於3秒）：").strip()
        try:
            delay = int(delay) if delay else 5
            if delay < 3:
                print("⚠️  間隔時間過短可能導致被封鎖，建議至少3秒")
                delay = max(delay, 3)
        except ValueError:
            delay = 5
        
        # 檢查關鍵字檔案是否存在，如果不存在則創建範例檔案
        if not os.path.exists(keywords_file):
            print(f"\n關鍵字檔案 {keywords_file} 不存在，正在創建範例檔案...")
            with open(keywords_file, 'w', encoding='utf-8') as f:
                f.write("# PTT 搜索關鍵字列表\n")
                f.write("# 每行一個關鍵字，以 # 開頭的行為註解\n")
                f.write("# 請編輯此檔案，添加您想搜索的關鍵字\n\n")
                f.write("Python\n")
                f.write("機器學習\n")
                f.write("股票\n")
                f.write("美食\n")
            print(f"已創建範例檔案 {keywords_file}")
            print("請編輯此檔案，添加您想搜索的關鍵字，然後重新執行程式")
        else:
            # 執行批量搜索
            batch_search_from_file(keywords_file, max_results, delay)
        
    else:
        # 單次搜索模式（原有功能）
        keyword = input("請輸入想搜尋的關鍵字：")
        max_results = input("要抓幾筆結果（預設 10）：")
        
        try:
            max_results = int(max_results) if max_results else 10
        except ValueError:
            max_results = 10
        
        data = search_via_multiple_engines(keyword, max_results)
        
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
            save_individual_results(data, keyword)
            
            # 累積保存到主要 JSON 檔案（去重功能）
            master_json_filename = "ptt_links_master.json"
            save_to_master_json(data, keyword, master_json_filename)
            
            print(f"結果已保存到：")
            print(f"  詳細結果：ptt_search_{keyword.replace(' ', '_').replace('/', '_')}.txt")
            print(f"  累積JSON：{master_json_filename}")
            print(f"  純連結：ptt_urls_{keyword.replace(' ', '_').replace('/', '_')}.txt")
        else:
            print("沒有找到相關的 PTT 連結")
            print("建議：")
            print("1. 嘗試不同的關鍵字")
            print("2. 直接到 PTT 網站搜尋")
            print(f"3. 手動搜尋：https://www.ptt.cc/bbs/search?q={urllib.parse.quote(keyword)}")
