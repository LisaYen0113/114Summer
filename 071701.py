from ckiptagger import data_utils
data_utils.download_data_gdown("./")

import requests
from bs4 import BeautifulSoup
from ckiptagger import WS, POS
import re

# 初始化 CKIPTagger
ws = WS("./data")
pos = POS("./data")

# 情緒詞庫（簡化版）
positive_words = {"支持", "讚", "加油", "認同", "真相", "公正"}
negative_words = {"抄襲", "1450", "綠營", "造謠", "噁心", "黑幕"}

def analyze_article(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    cookies = {'over18': '1'}
    res = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, "html.parser")

    # 抓標題
    meta_lines = soup.select("div.article-metaline")
    title = ""
    for meta in meta_lines:
        if "標題" in meta.text:
            title = meta.select("span.article-meta-value")[0].text
            break

    # 抓主文內容（排除標籤與推文）
    main_text = soup.select_one("#main-content").text
    content_lines = main_text.split("\n")
    content_lines = [line for line in content_lines if not line.startswith("※") and not re.match(r"^:|^推|^噓|^→", line)]
    content_text = " ".join(content_lines)

    # CKIP斷詞 + 詞性
    word_sentence = ws([content_text])[0]
    pos_sentence = pos([word_sentence])[0]
    important_pos = {'Na', 'Nb', 'Nc', 'Vt', 'VC', 'A'}
    keywords = [w for w, p in zip(word_sentence, pos_sentence) if p in important_pos]

    # 留言區處理
    pushes = soup.select("div.push")
    push_texts = []
    pos_count = 0
    neg_count = 0

    for push in pushes:
        push_content = push.select("span.push-content")
        if push_content:
            text = push_content[0].text.strip(": ")
            push_texts.append(text)
            # 情緒分類（簡易關鍵字比對）
            if any(word in text for word in positive_words):
                pos_count += 1
            elif any(word in text for word in negative_words):
                neg_count += 1

    push_combined = " ".join(push_texts)
    push_words = ws([push_combined])[0]
    push_pos = pos([push_words])[0]
    push_keywords = [w for w, p in zip(push_words, push_pos) if p in important_pos]

    # 輸出結果
    print(f"\n📌 標題：{title}")
    print(f"\n📄 主文關鍵詞：\n{keywords}")
    print(f"\n💬 留言關鍵詞：\n{push_keywords}")
    print(f"\n👍 支持推文數：{pos_count}　👎 批評推文數：{neg_count}　🤔 其他：{len(pushes) - pos_count - neg_count}")

analyze_article("https://www.ptt.cc/bbs/HatePolitics/M.1689453596.A.27B.html")
