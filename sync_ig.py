import os
import re
import requests

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
HTML_FILE = "index.html"

# 多分頁設定 (Travel 與 Project)
FEED_CONFIGS = [
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

# Gallery 類別設定
GALLERY_CONFIG = {
    "start_tag": "<!-- IG_GALLERY_POSTS_START -->",
    "end_tag": "<!-- IG_GALLERY_POSTS_END -->",
    "categories": [
        {"title": "Film Photo", "hashtags": ["#urbanwilderfilm"]},
        {"title": "Cat & Dog", "hashtags": ["#urbanwilderdog", "#urbanwildercat"]},
        {"title": "Bee & Wasp", "hashtags": ["#urbanwilderwasps", "#urbanwilderbees"]},
        {"title": "Butterfly", "hashtags": ["#urbanwilderbutterfly"]}
    ]
}

def fetch_ig_posts():
    print("開始抓取 Instagram 所有歷史貼文（含多張照片與自動翻頁）...")
    all_posts = []
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

    # ====== 1. 處理 Travel & Project Feed ======
    for config in FEED_CONFIGS:
        hashtag = config["hashtag"]
        start_tag = config["start_tag"]
        end_tag = config["end_tag"]
        
        cards_html = []
        unique_locations = set()
        post_count = 0

        for post in posts:
            caption = post.get('caption') or ''
            if hashtag not in caption:
                continue

            permalink = post.get('permalink', '')
            safe_title = caption.replace('\n', ' ')[:20]
            
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

            # 製作相片區塊 (Carousel)，強制套用 object-fit: contain
            photos_html_block = '<div class="feed-photo-carousel" style="width: 100%; height: 100%; display: flex; overflow-x: auto; scroll-snap-type: x mandatory;">'
            for img_url in image_urls:
                photos_html_block += f"""
                        <div class="feed-photo-item" style="flex: 0 0 100%; scroll-snap-align: start; position: relative; min-height: 280px; background-color: #f9f9f9;">
                            <img src="{img_url}" alt="Post Photo" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain;">
                        </div>
                """
            photos_html_block += '</div>'

            # 抓取地標
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

            post_html = f"""
                    <div class="feed-card" {loc_attr}>
                        <!-- 照片區塊 (強制在左邊) -->
                        <div class="feed-photo">
                            {photos_html_block}
                        </div>
                        
                        <!-- 文字區塊 (強制在右邊) -->
                        <div class="feed-content">
                            <div class="feed-header">
                                <h3><span class="en">{safe_title}...</span><span class="lang-zh">{safe_title}...</span></h3>
                            </div>
                            <div class="feed-desc">
                                {location_html}
                                <div class="feed-desc-text">
                                    <p style="margin: 0; text-align: left; font-size: 14px;">{formatted_caption}</p>
                                </div>
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

    # ====== 2. 處理 Gallery 區塊 ======
    gallery_html = ""
    for cat in GALLERY_CONFIG["categories"]:
        cat_title = cat["title"]
        cat_hashtags = cat["hashtags"]
        
        cat_posts = []
        for post in posts:
            caption = post.get('caption', '')
            if any(tag in caption for tag in cat_hashtags):
                cat_posts.append(post)
                
        if not cat_posts:
            continue
            
        gallery_html += f'                    <div class="gallery-category">\n'
        gallery_html += f'                        <h3>{cat_title}</h3>\n'
        gallery_html += f'                        <div class="gallery-carousel">\n'
        
        for post in cat_posts:
            permalink = post.get('permalink', '')
            img_url = ''
            
            # 取出第一張照片當封面即可
            if post.get('media_type') == 'CAROUSEL_ALBUM':
                children = post.get('children', {}).get('data', [])
                if children:
                    img_url = children[0].get('media_url', '')
            else:
                img_url = post.get('media_url', '')
                
            if not img_url:
                continue
                
            gallery_html += f'''                            <a href="{permalink}" target="_blank" class="gallery-item">
                                <img src="{img_url}" alt="{cat_title}">
                            </a>\n'''
                            
        gallery_html += f'                        </div>\n'
        gallery_html += f'                    </div>\n'

    pattern_gal = rf'({re.escape(GALLERY_CONFIG["start_tag"])})(.*?)({re.escape(GALLERY_CONFIG["end_tag"])})'
    if re.search(pattern_gal, file_data, flags=re.DOTALL):
        file_data = re.sub(pattern_gal, rf'\1\n{gallery_html}\n\3', file_data, flags=re.DOTALL)
    else:
        print(f"❌ 錯誤：找不到 Gallery Start Tag")

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(file_data)
    print("✅ 全部 HTML 檔案更新完畢！")

if __name__ == "__main__":
    update_html()
