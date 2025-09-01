Dcard 的網頁是使用 React 前端框架搭配動態載入（SPA）

是不是整頁都看不到 標題、內容、留言？
➡️ 這是因為它是用 JavaScript 動態渲染的（React）
➡️ 網頁初始載入幾乎沒有實際資料，要跑 JS 才會出現

F12 開開發者工具
點「Network」標籤 → Reload 頁面
過濾關鍵字：posts
這些請求的 response 才是「真正的資料來源」
（就是用 API 拿的 JSON 資料）