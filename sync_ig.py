import os
import re
import requests

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
HTML_FILE = "index.html"

# 多分頁設定 (Travel 與 Project)
CONFIGS = [
    {
        "hashtag": "#urbanwildertravel",
        "start_tag": "<!-- IG_TRAVEL_POSTS_START -->",
        "end_tag": "<!-- IG_TRAVEL_POSTS_END -->"
    },
    {
        "hashtag": "#urbanwilderproject",
        "start_tag": "<!-- IG_PROJECT_POSTS_START -->",
        "end_tag": "<!-- IG_PROJECT_POSTS_END -->"
    }
]

def fetch_ig_posts():
    print("開始抓取 Instagram 所有歷史貼文（含自動翻頁）...")
    all_posts = []
    # 設定 limit=100 加快抓取，並透過 while url 自動抓取更久以前的歷史貼文
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media?fields=id,caption,media_url,permalink,timestamp&access_token={ACCESS_TOKEN}&limit=100"
    
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print("❌ 抓取失敗：", response.text)
            break
        
        data = response.json()
        posts = data.get('data', [])
        all_posts.extend(posts)
        print(f"已累計抓取 {len(all_posts)} 篇貼文...")
        
        # 檢查是否有下一頁 (Pagination)，若有則繼續抓取更舊的貼文
        paging = data.get('paging', {})
        url = paging.get('next')
        
    print(f"歷史貼文抓取完畢，總共取得 {len(all_posts)} 篇貼文。")
    return all_posts

def update_html():
    posts = fetch_ig_posts()
    
    # 讀取原本的 HTML 檔案
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        file_data = f.read()

    # 針對每一個分類進行處理
    for config in CONFIGS:
        hashtag = config["hashtag"]
        start_tag = config["start_tag"]
        end_tag = config["end_tag"]
        
        generated_html = '\n<div class="feed-list">\n'
        post_count = 0

        for post in posts:
            caption = post.get('caption', '')
            if hashtag not in caption:
                continue

            media_url = post.get('media_url', '')
            permalink = post.get('permalink', '')
            safe_title = caption.replace('\n', ' ')[:20]
            formatted_caption = caption.replace('\n', '<br>')

            post_html = f"""
                    <a href="{permalink}" target="_blank" class="feed-card">
                        <div class="feed-photo">
                            <img src="{media_url}" alt="Post Photo">
                        </div>
                        <div class="feed-content">
                            <div class="feed-header">
                                <h3><span class="en">{safe_title}...</span><span class="lang-zh">{safe_title}...</span></h3>
                            </div>
                            <div class="feed-desc">
                                <p style="margin: 0; text-align: left; font-size: 14px;">{formatted_caption}</p>
                            </div>
                            <div class="feed-footer">
                                <img src="Image/Profile.jpeg" alt="Avatar" class="feed-avatar">
                                <span class="en">View on Instagram</span><span class="lang-zh">在 IG 上查看</span>
                            </div>
                        </div>
                    </a>
            """
            generated_html += post_html
            post_count += 1

        generated_html += '</div>\n'
        print(f"[{hashtag}] 處理完畢，共找到 {post_count} 篇符合的貼文。")

        # 寫入 HTML
        pattern = rf"({re.escape(start_tag)})(.*?)({re.escape(end_tag)})"
        if re.search(pattern, file_data, flags=re.DOTALL):
            file_data = re.sub(pattern, rf"\1{generated_html}\3", file_data, flags=re.DOTALL)
        else:
            print(f"❌ 錯誤：找不到 {start_tag}")

    # 存檔
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(file_data)
    print("✅ 全部 HTML 檔案更新完畢！")

if __name__ == "__main__":
    update_html()
