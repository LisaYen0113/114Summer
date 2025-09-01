#爬公視即時新聞

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

options = Options() #設定瀏覽器啟動的選項
# options.add_argument("--headless")  # 若不需看到畫面可打開這行（抓資料更快，但不利 debug）

driver = webdriver.Chrome(options=options)
driver.get("https://news.pts.org.tw/dailynews/")

# 模擬向下捲動頁面（共捲 5 次）
for _ in range(1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #用 JavaScript 模擬瀏覽器滾動到底部
    time.sleep(1) #等待每次滾動後的新聞載入

#soup:用來查詢 HTML 元素的 BeautifulSoup 物件。
soup = BeautifulSoup(driver.page_source, "html.parser") #取得目前網頁的完整 HTML 原始碼。取得目前網頁的完整 HTML 原始碼。
news_items = soup.select("li.d-flex")

print("共抓到新聞：", len(news_items))
print("-" * 40)

for item  in news_items[:10]:  # 取前10筆
    # 標題與連結
    title_tag = item.select_one("h2 a")
    title = title_tag.text.strip()
    url = title_tag["href"]

    # 發布時間
    time_tag = item.select_one("time")
    publish_time = time_tag.text.strip() if time_tag else "無時間資訊"

    # 分類（例如：全球）
    category_tag = item.select_one(".news-info a[href*='/category/']")
    category = category_tag.text.strip() if category_tag else "無分類"

    # 標籤（例如：政治人物、川普遇刺...）
    tag_tags = item.select("ul.tag-list li.gray-tag.hashList a")
    tags = [tag.text.strip() for tag in tag_tags]
    
    
    print("標題：", title)
    print("連結：", url)
    print("時間：", time)
    print("分類：", category)
    print("標籤：", tags)
    print("-" * 50)
    

    # 開新分頁打開文章連結
    driver.get(url)
    time.sleep(1.5)  # 保守等待內頁載入（可調整）

    detail_soup = BeautifulSoup(driver.page_source, "html.parser")

    # 文章內文
    content_div = detail_soup.select_one("div.post-article")
    if content_div:
        img_caption = content_div.select_one("div.articleimg")
        img_text = img_caption.text.strip() if img_caption else ""

        paragraphs = content_div.find_all("p")
        para_text = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

        article = img_text + "\n" + para_text if img_text else para_text
    else:
        article = "無內文"

    # 發布時間
    time_tag = detail_soup.select_one("div.article-time time")
    publish_time = time_tag.text.strip() if time_tag else "無發布時間"

    # 標籤
    tag_elements = detail_soup.select("ul.tag-list li a")
    tags = [tag.text.strip() for tag in tag_elements]

    # 作者
    author_tag = detail_soup.select_one("div.article_authors a")
    author = author_tag.text.strip() if author_tag else "無作者資訊"

    print("作者：", author)
    print("發布時間：", publish_time)
    print("標籤：", tags)
    print("內文：", article)

    print("-" * 40)
     
driver.quit()


'''
<li class="d-flex">
    <figure style="padding-bottom: 8px">
        <a href="https://news.pts.org.tw/article/760488" class="useImgHover">
            <div class="embed-responsive embed-responsive-16by9">
                <div class="embed-responsive-item">
                    <img class="cover-fit" loading="lazy"
                        src="https://news-data.pts.org.tw/media/240415/conversions/cover-thumb.jpg" data-fallback=""
                        onerror="this.src = this.dataset.fallback; this.onerror = null;">
                </div>
            </div>
        </a>
    </figure>
    <div>
        <h2 title="川普遇槍擊滿週年 專家：政治狂言有激化暴力趨勢"><a href="https://news.pts.org.tw/article/760488">川普遇槍擊滿週年 專家：政治狂言有激化暴力趨勢</a>
        </h2>
        <div class="news-info news-info-update">

            <time datetime="2025-07-11 20:27:07">
                2025/7/11 20:27</time>
            <span>|</span>
            <a href="https://news.pts.org.tw/category/4">全球</a>

        </div>
        <ul x-data="articleTags" class="list-unstyled tag-list list-flex d-flex" create-time="2025-07-11 20:27:07"
            x-ref="list">
            <li class="gray-tag hashList"><a href="/tag/29863/">政治人物</a></li>

            <li class="gray-tag hashList"><a href="/tag/35436/">川普遇刺</a></li>

            <li class="gray-tag hashList"><a href="/tag/3247/">暴力</a></li>

            <li class="gray-tag hashList"><a href="/tag/19939/">政治</a></li>
            <li @click="show" x-show="showMore" class="gray-tag"><a>...</a></li>

            <li class="gray-tag hide-tag hashList"><a href="/tag/22547/">國會議員</a></li>

        </ul>


    </div>
</li>
'''