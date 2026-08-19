import os
import re
import requests

# 從 GitHub Secrets 取得金鑰
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

TARGET_HASHTAG = "#urbanwildertravel"
HTML_FILE = "index.html"  # 確保這是你網頁檔案的正確名稱

def fetch_ig_posts():
    print("開始抓取 Instagram 貼文...")
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media?fields=id,caption,media_url,permalink,timestamp&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ 抓取失敗，請檢查 Token 是否過期或正確：", response.text)
        return []
    return response.json().get('data', [])

def update_html():
    posts = fetch_ig_posts()
    generated_html = '\n<div class="feed-list">\n'
    post_count = 0

    for post in posts:
        caption = post.get('caption', '')
        
        # 檢查是否包含特定 Hashtag
        if TARGET_HASHTAG not in caption:
            continue

        media_url = post.get('media_url', '')
        permalink = post.get('permalink', '')
        
        # 處理標題 (取前20個字當標題)
        safe_title = caption.replace('\n', ' ')[:20]
        
        # 處理內文換行，避免破壞 HTML
        formatted_caption = caption.replace('\n', '<br>')

        # 組合 HTML 卡片
        post_html = f"""
                    <a href="{permalink}" target="_blank" class="feed-card">
                        <div class="feed-photo">
                            <img src="{media_url}" alt="Travel Photo">
                        </div>
                        <div class="feed-content">
                            <div class="feed-header">
                                <h3>
                                    <span class="en">{safe_title}...</span>
                                    <span class="lang-zh">{safe_title}...</span>
                                </h3>
                            </div>
                            <div class="feed-desc">
                                <p style="margin: 0; text-align: left; font-size: 14px;">
                                    {formatted_caption}
                                </p>
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

    if post_count == 0:
        print(f"⚠️ 沒有找到包含 {TARGET_HASHTAG} 的貼文。")
        return

    # 讀取原本的 HTML 檔案
    print(f"準備寫入 HTML，共找到 {post_count} 篇旅遊貼文...")
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        file_data = f.read()

    # 使用正則表達式替換標記之間的內容
    pattern = r"(<!-- IG_TRAVEL_POSTS_START -->)(.*?)(<!-- IG_TRAVEL_POSTS_END -->)"
    
    if re.search(pattern, file_data, flags=re.DOTALL):
        new_data = re.sub(pattern, rf"\1{generated_html}\3", file_data, flags=re.DOTALL)
        
        # 寫回 HTML 檔案
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_data)
        print("✅ 成功！HTML 檔案已經自動更新完畢！")
    else:
        print("❌ 錯誤：在 HTML 中找不到 <!-- IG_TRAVEL_POSTS_START --> 標記。")

if __name__ == "__main__":
    update_html()
