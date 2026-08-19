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
    print("開始抓取 Instagram 所有歷史貼文（含多張照片與自動翻頁）...")
    all_posts = []
    # 透過 children{media_url} 抓取多張輪播照片，並用 while url 自動翻頁
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media?fields=id,caption,media_url,permalink,timestamp,media_type,children{{media_url}}&access_token={ACCESS_TOKEN}&limit=100"
    
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print("❌ 抓取失敗：", response.text)
            break
        
        data = response.json()
        posts = data.get('data', [])
        all_posts.extend(posts)
        print(f"已累計抓取 {len(all_posts)} 篇貼文...")
        
        paging = data.get('paging', {})
        url = paging.get('next')
        
    print(f"歷史貼文抓取完畢，總共取得 {len(all_posts)} 篇貼文。")
    return all_posts

def update_html():
    posts = fetch_ig_posts()
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        file_data = f.read()

    for config in CONFIGS:
        hashtag = config["hashtag"]
        start_tag = config["start_tag"]
        end_tag = config["end_tag"]
        
        cards_html = []
        unique_locations = set() # 收集所有出現過的地點
        post_count = 0

        for post in posts:
            caption = post.get('caption', '')
            if hashtag not in caption:
                continue

            permalink = post.get('permalink', '')
            safe_title = caption.replace('\n', ' ')[:20]
            
            # 收集這篇貼文的所有圖片（支援單張或多張 Carousel 輪播照片）
            image_urls = []
            media_type = post.get('media_type', '')
            
            if media_type == 'CAROUSEL_ALBUM':
                children = post.get('children', {}).get('data', [])
                for child in children:
                    child_url = child.get('media_url')
                    if child_url:
                        image_urls.append(child_url)
            
            if not image_urls and post.get('media_url'):
                image_urls.append(post.get('media_url'))

            # 🌟 製作水平滑動的相片輪播容器 (Carousel)
            photos_html_block = '<div class="feed-photo-carousel">'
            for img_url in image_urls:
                photos_html_block += f"""
                        <div class="feed-photo-item">
                            <img src="{img_url}" alt="Post Photo">
                        </div>
                """
            photos_html_block += '</div>'

            # 抓取 "📍 | 後面的文字" 作為地標 (排除 Hashtags 以免文字過長)
            location_match = re.search(r'📍\s*\|\s*([^\n\r]+)', caption)
            if location_match:
                location_name = location_match.group(1).split('#')[0].strip()
                unique_locations.add(location_name)
                loc_attr = f'data-location="{location_name}"'
                location_html = f'''
                    <div style="font-size: 13px; color: var(--accent); margin-bottom: 8px; font-weight: bold;">
                        <i class="fa-solid fa-location-dot"></i> {location_name}
                    </div>
                '''
            else:
                loc_attr = 'data-location="unknown"'
                location_html = ''

            formatted_caption = caption.replace('\n', '<br>')

            # 🌟 組合卡片 HTML (加入多圖輪播、動態地點標籤與 Show more 按鈕)
            post_html = f"""
                    <div class="feed-card" {loc_attr} style="flex-direction: column; align-items: stretch;">
                        {photos_html_block}
                        <div class="feed-content" style="width: 100%; box-sizing: border-box;">
                            <div class="feed-header">
                                <h3><span class="en">{safe_title}...</span><span class="lang-zh">{safe_title}...</span></h3>
                            </div>
                            <div class="feed-desc">
                                {location_html}
                                <!-- 內文折疊區塊 -->
                                <div class="feed-desc-text">
                                    <p style="margin: 0; text-align: left; font-size: 14px;">{formatted_caption}</p>
                                </div>
                                <!-- 展開/收起 按鈕 -->
                                <button class="read-more-btn" onclick="toggleReadMore(this)">
                                    <span class="en">Show more...</span><span class="lang-zh">顯示更多...</span>
                                </button>
                            </div>
                            <div class="feed-footer" style="margin-top: 15px;">
                                <img src="Image/Profile.jpeg" alt="Avatar" class="feed-avatar">
                                <a href="{permalink}" target="_blank" style="color: var(--accent); text-decoration: none; font-weight: bold;">
                                    <span class="en">View on Instagram</span><span class="lang-zh">在 IG 上查看</span>
                                </a>
                            </div>
                        </div>
                    </div>
            """
            cards_html.append(post_html)
            post_count += 1

        # 如果是旅遊分頁，自動生成「地區分類」下拉選單
        dropdown_html = ""
        if hashtag == "#urbanwildertravel" and unique_locations:
            options = '<option value="all">All Locations / 全部地區</option>\n'
            for loc in sorted(unique_locations):
                options += f'                    <option value="{loc}">{loc}</option>\n'
            
            dropdown_html = f"""
            <div class="content-dropdown-wrapper" style="margin-bottom: 25px;">
                <select class="content-select" onchange="filterTravelLocation(this.value)">
{options}                </select>
            </div>
            """

        generated_html = dropdown_html + '\n<div class="feed-list">\n' + "".join(cards_html) + '\n</div>\n'
        print(f"[{hashtag}] 處理完畢，共找到 {post_count} 篇符合的貼文。")

        pattern = rf"({re.escape(start_tag)})(.*?)({re.escape(end_tag)})"
        if re.search(pattern, file_data, flags=re.DOTALL):
            file_data = re.sub(pattern, rf"\1\n{generated_html}\n\3", file_data, flags=re.DOTALL)
        else:
            print(f"❌ 錯誤：找不到 {start_tag}")

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(file_data)
    print("✅ 全部 HTML 檔案更新完畢！")

if __name__ == "__main__":
    update_html()
