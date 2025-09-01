#民視最新新聞

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

options = Options()
# options.add_argument("--headless")  # 若不需看到畫面可打開這行（抓資料更快，但不利 debug）

driver = webdriver.Chrome(options=options)
driver.get("https://www.ftvnews.com.tw/realtime/")

# 模擬向下捲動頁面（共捲 5 次）
for _ in range(1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #用 JavaScript 模擬瀏覽器滾動到底部
    time.sleep(1) #等待每次滾動後的新聞載入

soup = BeautifulSoup(driver.page_source, "html.parser")
news_cards = soup.select(".news-block")

print("共抓到新聞：", len(news_cards))
print("-" * 40)

for card in news_cards[:10]:  # 取前10筆
    title = card.select_one("h2.title").text.strip() #.text.strip() 是去除前後空白
    desc = card.select_one("div.desc").text.strip()
    relative_url = card.select_one("a[href]")["href"]
    full_url = "https://www.ftvnews.com.tw" + relative_url

    print("📰 標題：", title)
    print("📄 摘要：", desc)
    print("🔗 連結：", full_url)

    # 開新分頁打開文章連結
    driver.get(full_url)
    time.sleep(1.5)  # 保守等待內頁載入（可調整）

    detail_soup = BeautifulSoup(driver.page_source, "html.parser")
    content_div = detail_soup.select_one("#preface")
    if content_div:
        paragraphs = content_div.find_all("p")
        article = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        print("📜 內文：", article)
    else:
        print("⚠️ 沒找到 #preface")

    content_div2 = detail_soup.select_one("#newscontent")
    if content_div2:
        paragraphs2 = content_div2.find_all("p")
        article2 = "\n".join([p.text.strip() for p in paragraphs2 if p.text.strip()])
        print("📜 內文2：", article2)
    else:
        print("⚠️ 沒找到 #newscontent")

    
    # 找到 ul 標籤中 id 是 Lit_shareTop 的區塊
    time_list = detail_soup.select("ul#Lit_shareTop span.date")

    # 印出每一個時間資訊
    for span in time_list:
        print(span.text.strip())
        
    print("-" * 40)
     
driver.quit()


'''
<li class="rl-list col-12">
    <div class="news-block"> <a class="img-block" href="/news/detail/2025712W0030"> <img loading="lazy"
                src="https://cdn.ftvnews.com.tw/manasystem/FileData/News/1/a017474e-367e-4449-b13f-ae6e99461ae6.jpg"
                alt="快新聞／印度航空波音787墜機260死！　初步調查結果出爐了"> </a>
        <div class="content"> <a href="/news/detail/2025712W0030">
                <div class="time" data-time="2025/07/12 07:39:51">4 分鐘前</div>
                <h2 class="title">快新聞／印度航空波音787墜機260死！　初步調查結果出爐了</h2>
                <div class="desc">
                    即時中心／林耿郁報導6月12日，印度航空一架波音787夢幻客機，剛剛從機場起飛就墜落，造成260人不幸死亡；事故過去一個月，今（12）天印度方面發表初步調查結果，原因是兩台引擎不明原因遭到關閉，而且並未發現鳥擊或燃油汙染等狀況存在。
                </div>
            </a>
            <div class="share-btn">
                <ul>
                    <li><a class="share_fb" href="javascript:;" data-type="facebook"
                            data-url="https://www.ftvnews.com.tw/news/detail/2025712W0030"
                            data-title="快新聞／印度航空波音787墜機260死！　初步調查結果出爐了 - 民視新聞網"><i
                                class="fab fa-facebook-square"></i></a></li>
                    <li><a class="share_twt" href="javascript:;" data-type="twitter"
                            data-url="https://www.ftvnews.com.tw/news/detail/2025712W0030"
                            data-title="快新聞／印度航空波音787墜機260死！　初步調查結果出爐了 - 民視新聞網"><i
                                class="fa-brands fa-square-x-twitter"></i></a></li>
                    <li><a class="share_line" href="javascript:;" data-type="line"
                            data-url="https://www.ftvnews.com.tw/news/detail/2025712W0030"
                            data-title="快新聞／印度航空波音787墜機260死！　初步調查結果出爐了 - 民視新聞網"><i class="fab fa-line"></i></a></li>
                </ul>
            </div>
        </div>
    </div>
</li>
'''