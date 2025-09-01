#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
替代搜尋方法 - 使用不同的搜尋策略
"""

import requests
import json
import urllib.parse
import time

def search_via_searx(query, max_results=10):
    """
    使用 SearX 搜尋引擎 (開源搜尋引擎)
    """
    results = []
    
    # SearX 公共實例
    searx_instances = [
        "https://searx.be",
        "https://search.sapti.me",
        "https://searx.info"
    ]
    
    search_query = f"{query} site:ptt.cc"
    
    for instance in searx_instances:
        try:
            print(f"嘗試 SearX 實例: {instance}")
            
            params = {
                'q': search_query,
                'format': 'json',
                'engines': 'google,bing,duckduckgo'
            }
            
            response = requests.get(f"{instance}/search", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for result in data.get('results', []):
                    url = result.get('url', '')
                    title = result.get('title', '')
                    
                    if 'ptt.cc' in url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'source': f'SearX ({instance})'
                        })
                        print(f"找到: {title}")
                        
                        if len(results) >= max_results:
                            return results
                            
            time.sleep(1)
            
        except Exception as e:
            print(f"SearX 錯誤 ({instance}): {e}")
            continue
    
    return results

def search_via_startpage(query, max_results=10):
    """
    使用 Startpage 搜尋
    """
    results = []
    
    try:
        print("嘗試 Startpage 搜尋...")
        
        search_query = f"{query} site:ptt.cc"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://www.startpage.com/sp/search?query={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 簡單的文字搜尋
            content = response.text
            
            # 尋找 PTT 連結
            import re
            ptt_links = re.findall(r'https?://[^"\s]*ptt\.cc[^"\s]*', content)
            
            for link in ptt_links[:max_results]:
                results.append({
                    'title': f'PTT文章 - {link.split("/")[-1] if "/" in link else link}',
                    'url': link,
                    'source': 'Startpage'
                })
                print(f"Startpage 找到: {link}")
                
    except Exception as e:
        print(f"Startpage 搜尋錯誤: {e}")
    
    return results

def create_direct_ptt_urls(query):
    """
    創建直接的 PTT 搜尋 URL
    """
    encoded_query = urllib.parse.quote(query)
    
    direct_urls = [
        {
            'title': f'PTT全站搜尋: {query}',
            'url': f'https://www.ptt.cc/bbs/search?q={encoded_query}',
            'description': '直接在PTT網站搜尋'
        },
        {
            'title': f'PTT看板搜尋: home-sale',
            'url': f'https://www.ptt.cc/bbs/home-sale/search?q={encoded_query}',
            'description': '房屋買賣板搜尋'
        },
        {
            'title': f'PTT看板搜尋: NewTaipei',
            'url': f'https://www.ptt.cc/bbs/NewTaipei/search?q={encoded_query}',
            'description': '新北市板搜尋'
        },
        {
            'title': f'PTT看板搜尋: Lifeismoney',
            'url': f'https://www.ptt.cc/bbs/Lifeismoney/search?q={encoded_query}',
            'description': '省錢板搜尋'
        },
        {
            'title': f'PTT看板搜尋: ask',
            'url': f'https://www.ptt.cc/bbs/ask/search?q={encoded_query}',
            'description': '問答板搜尋'
        }
    ]
    
    return direct_urls

def generate_google_search_urls(query):
    """
    生成 Google 搜尋 URL
    """
    search_variations = [
        f"{query} site:ptt.cc",
        f"板橋 生活 site:ptt.cc",
        f"板橋區 環境 site:ptt.cc",
        f"板橋 居住 心得 site:ptt.cc",
        f"新北 板橋 site:ptt.cc"
    ]
    
    google_urls = []
    for search in search_variations:
        encoded = urllib.parse.quote(search)
        google_urls.append({
            'title': f'Google搜尋: {search}',
            'url': f'https://www.google.com/search?q={encoded}',
            'description': f'在Google搜尋: {search}'
        })
    
    return google_urls

def main():
    """主程式"""
    query = "板橋區 生活環境"
    print(f"使用替代方法搜尋: {query}")
    print("=" * 60)
    
    all_results = []
    
    # 方法1: SearX 搜尋
    print("方法1: 使用 SearX 搜尋引擎")
    searx_results = search_via_searx(query, 5)
    all_results.extend(searx_results)
    
    # 方法2: Startpage 搜尋
    print("\n方法2: 使用 Startpage 搜尋")
    startpage_results = search_via_startpage(query, 5)
    all_results.extend(startpage_results)
    
    # 方法3: 直接 PTT URL
    print("\n方法3: 直接 PTT 搜尋連結")
    direct_urls = create_direct_ptt_urls(query)
    
    # 方法4: Google 搜尋 URL
    print("方法4: Google 搜尋連結")
    google_urls = generate_google_search_urls(query)
    
    # 顯示結果
    print(f"\n自動搜尋結果 ({len(all_results)} 個):")
    print("-" * 40)
    for i, result in enumerate(all_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   來源: {result['source']}")
        print()
    
    print("直接PTT搜尋連結:")
    print("-" * 40)
    for i, url in enumerate(direct_urls, 1):
        print(f"{i}. {url['title']}")
        print(f"   {url['url']}")
        print(f"   {url['description']}")
        print()
    
    print("Google搜尋連結:")
    print("-" * 40)
    for i, url in enumerate(google_urls, 1):
        print(f"{i}. {url['title']}")
        print(f"   {url['url']}")
        print()
    
    # 保存所有結果
    with open('alternative_search_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"板橋區生活環境搜尋結果\n")
        f.write("=" * 50 + "\n\n")
        
        if all_results:
            f.write("自動搜尋結果:\n")
            f.write("-" * 30 + "\n")
            for i, result in enumerate(all_results, 1):
                f.write(f"{i}. {result['title']}\n")
                f.write(f"   {result['url']}\n")
                f.write(f"   來源: {result['source']}\n\n")
        
        f.write("直接PTT搜尋連結:\n")
        f.write("-" * 30 + "\n")
        for i, url in enumerate(direct_urls, 1):
            f.write(f"{i}. {url['title']}\n")
            f.write(f"   {url['url']}\n")
            f.write(f"   {url['description']}\n\n")
        
        f.write("Google搜尋連結:\n")
        f.write("-" * 30 + "\n")
        for i, url in enumerate(google_urls, 1):
            f.write(f"{i}. {url['title']}\n")
            f.write(f"   {url['url']}\n\n")
    
    print(f"所有結果已保存到 alternative_search_results.txt")
    
    if not all_results:
        print("\n建議:")
        print("1. 直接點擊上述 PTT 搜尋連結")
        print("2. 使用 Google 搜尋連結")
        print("3. 手動到 PTT 網站搜尋")

if __name__ == "__main__":
    main()