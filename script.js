// 1. 選單展開/收合控制
function toggleMenu() {
    const nav = document.getElementById('main-nav');
    if (nav.style.display === 'flex') {
        nav.style.display = 'none'; 
    } else {
        nav.style.display = 'flex'; 
    }
}

function toggleSub(event) {
    event.preventDefault();
    event.stopPropagation();
    const clickedNavItem = event.target.closest('.nav-item');
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item !== clickedNavItem) {
            item.classList.remove('expanded');
        }
    });
    if (clickedNavItem) {
        clickedNavItem.classList.toggle('expanded');
    }
}

// 2. 語言切換設定（新增 localStorage 跨頁記憶功能）
let currentLang = localStorage.getItem('siteLang') || 'en';

function applyLanguage(lang) {
    const body = document.body;
    if (lang === 'zh') {
        body.classList.remove('lang-en');
        body.classList.add('lang-zh');
        currentLang = 'zh';
    } else {
        body.classList.remove('lang-zh');
        body.classList.add('lang-en');
        currentLang = 'en';
    }
}

function toggleLanguage() {
    const newLang = currentLang === 'en' ? 'zh' : 'en';
    localStorage.setItem('siteLang', newLang);
    applyLanguage(newLang);
}

window.addEventListener('DOMContentLoaded', () => {
    applyLanguage(currentLang);
});

// 3. 旅遊地點篩選與相機篩選
function filterTravelLocation(location) {
    const cards = document.querySelectorAll('.feed-card');
    cards.forEach(card => {
        if (location === 'all' || card.getAttribute('data-location') === location) {
            card.style.display = ''; 
        } else {
            card.style.display = 'none'; 
        }
    });
}

function showCameraItem(cameraId) {
    if (cameraId === 'all') {
        document.getElementById('camera-select').scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }
    const targetCard = document.querySelector(`[data-camera="${cameraId}"]`);
    if (targetCard) {
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// 4. Read More 展開/收合
function toggleReadMore(btn) {
    const textContainer = btn.previousElementSibling;
    if (textContainer.classList.contains('expanded')) {
        textContainer.classList.remove('expanded');
        btn.innerHTML = '<span class="en">Show more...</span><span class="lang-zh">顯示更多...</span>';
    } else {
        textContainer.classList.add('expanded');
        btn.innerHTML = '<span class="en">Show less</span><span class="lang-zh">顯示更少</span>';
    }
    applyLanguage(currentLang);
}

function checkReadMoreButtons() {
    setTimeout(() => {
        document.querySelectorAll('.feed-desc-text').forEach(el => {
            const btn = el.nextElementSibling;
            if (btn && btn.classList.contains('read-more-btn')) {
                if (el.scrollHeight > el.clientHeight) {
                    btn.style.display = 'inline-block';
                } else {
                    if (!el.classList.contains('expanded')) {
                        btn.style.display = 'none';
                    }
                }
            }
        });
    }, 100);
}

// 5. 自動擷取 IG 貼文第一句作為標題，並從內文中移除
function autoGenerateBlogTitles() {
    const feedCards = document.querySelectorAll('.feed-card');

    feedCards.forEach(card => {
        const pElement = card.querySelector('.feed-desc-text p');
        const headerH3 = card.querySelector('.feed-header h3');

        if (pElement && headerH3) {
            const htmlContent = pElement.innerHTML;
            const rawLines = htmlContent.split(/(<br\s*\/?>)/i); 
            
            let firstSentence = "";
            let targetIndex = -1;

            for (let i = 0; i < rawLines.length; i++) {
                if (rawLines[i].toLowerCase().includes('<br')) continue;

                let textLine = rawLines[i].replace(/<[^>]*>?/gm, '').trim();
                
                if (textLine && textLine !== '.') {
                    firstSentence = textLine;
                    targetIndex = i;
                    break;
                }
            }

            if (firstSentence) {
                const maxLength = 30;
                let displayTitle = firstSentence.length > maxLength 
                    ? firstSentence.substring(0, maxLength) + "..." 
                    : firstSentence;
                headerH3.innerHTML = `<span class="en">${displayTitle}</span><span class="lang-zh">${displayTitle}</span>`;

                rawLines[targetIndex] = rawLines[targetIndex].replace(firstSentence, '');

                for (let j = 0; j < targetIndex; j++) {
                   if (rawLines[j].replace(/<[^>]*>?/gm, '').trim() === '.') {
                       rawLines[j] = '';
                   }
                }
                
                let newHtml = rawLines.join('');
                newHtml = newHtml.replace(/^(\s*<br\s*\/?>\s*)+/gi, '');
                pElement.innerHTML = newHtml;
            }
        }
    });
}
window.addEventListener('load', autoGenerateBlogTitles);
window.addEventListener('load', checkReadMoreButtons);
window.addEventListener('resize', checkReadMoreButtons);

// 點擊外部關閉懸浮選單
document.addEventListener('click', function(event) {
    const nav = document.getElementById('main-nav');
    const menuBtn = document.getElementById('floating-menu-btn');
    if (nav && menuBtn && nav.classList.contains('dropdown-mode') && nav.style.display === 'flex') {
        if (!nav.contains(event.target) && !menuBtn.contains(event.target)) {
            nav.style.display = 'none';
        }
    }
    document.querySelectorAll('.nav-item.expanded').forEach(item => {
        if (!item.contains(event.target)) {
            item.classList.remove('expanded');
        }
    });
});

// 6. 常駐自訂進度滑桿
function initGalleryPermanentScrollbars() {
    const carousels = document.querySelectorAll('.gallery-carousel, .feed-photo-carousel');

    carousels.forEach(carousel => {
        if (carousel.nextElementSibling && carousel.nextElementSibling.classList.contains('custom-scrollbar-track')) {
            return;
        }

        const track = document.createElement('div');
        track.className = 'custom-scrollbar-track';
        track.style.cursor = 'pointer';

        const thumb = document.createElement('div');
        thumb.className = 'custom-scrollbar-thumb';
        thumb.style.touchAction = 'none';
        track.appendChild(thumb);

        carousel.parentNode.insertBefore(track, carousel.nextSibling);

        function updateThumb() {
            const scrollWidth = carousel.scrollWidth;
            const clientWidth = carousel.clientWidth;
            const scrollLeft = carousel.scrollLeft;

            if (scrollWidth <= clientWidth) {
                track.style.display = 'none';
                return;
            } else {
                track.style.display = 'block'; 
            }

            const visibleRatio = Math.max(clientWidth / scrollWidth, 0.2);
            thumb.style.width = (visibleRatio * 100) + '%';

            const maxScroll = scrollWidth - clientWidth;
            const scrollPercent = maxScroll > 0 ? scrollLeft / maxScroll : 0;
            const maxThumbTravel = track.clientWidth - thumb.clientWidth;
            thumb.style.transform = `translateX(${scrollPercent * maxThumbTravel}px)`;
        }

        carousel.addEventListener('scroll', updateThumb, { passive: true });
        window.addEventListener('resize', updateThumb);
        setTimeout(updateThumb, 300);

        let isDragging = false;
        let startX;
        let initialScrollLeft;

        function onDragStart(e) {
            isDragging = true;
            startX = e.type.includes('mouse') ? e.pageX : e.touches[0].pageX;
            initialScrollLeft = carousel.scrollLeft;
            document.body.style.userSelect = 'none';
        }

        function onDragMove(e) {
            if (!isDragging) return;
            e.preventDefault();
            
            const currentX = e.type.includes('mouse') ? e.pageX : e.touches[0].pageX;
            const walk = currentX - startX;
            
            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            const maxThumbTravel = track.clientWidth - thumb.clientWidth;
            const ratio = maxScroll / maxThumbTravel;
            
            carousel.scrollLeft = initialScrollLeft + (walk * ratio);
        }

        function onDragEnd() {
            isDragging = false;
            document.body.style.userSelect = '';
        }

        thumb.addEventListener('mousedown', onDragStart);
        thumb.addEventListener('touchstart', onDragStart, { passive: true });

        document.addEventListener('mousemove', onDragMove, { passive: false });
        document.addEventListener('touchmove', onDragMove, { passive: false });
        document.addEventListener('mouseup', onDragEnd);
        document.addEventListener('touchend', onDragEnd);

        track.addEventListener('click', (e) => {
            if (e.target === thumb) return;
            
            const trackRect = track.getBoundingClientRect();
            const clickX = e.clientX - trackRect.left;
            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            const maxThumbTravel = track.clientWidth - thumb.clientWidth;
            
            let scrollPercent = (clickX - thumb.clientWidth / 2) / maxThumbTravel;
            scrollPercent = Math.max(0, Math.min(1, scrollPercent));
            
            carousel.scrollTo({
                left: scrollPercent * maxScroll,
                behavior: 'smooth'
            });
        });
    });
}
window.addEventListener('load', initGalleryPermanentScrollbars);

// 7. 初始化 Gallery 燈箱效果 (Lightbox) 
function initLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) return;
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxIgLink = document.getElementById('lightbox-ig-link');

    galleryItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const imgSrc = this.querySelector('img').src;
            const igUrl = this.getAttribute('href');
            
            lightboxImg.src = imgSrc;
            lightboxIgLink.href = igUrl;
            
            lightbox.classList.add('show');
            document.body.style.overflow = 'hidden'; 
        });
    });
}

function closeLightbox(e) {
    if (e.target.id === 'lightbox-img' || e.target.closest('.lightbox-btn')) return;
    
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('show');
        document.body.style.overflow = '';
    }
}

window.addEventListener('load', initLightbox);

// 8. 接收外部連結 (如 IG Bio) 的跳轉指令 (相容舊的 #travel, #gallery, #project 暗號)
window.addEventListener('load', function() {
    const hash = window.location.hash;
    if (hash === '#travel') {
        window.location.href = 'TravelBlog.html';
    } else if (hash === '#gallery') {
        window.location.href = 'MyGallery.html';
    } else if (hash === '#project') {
        window.location.href = 'Project.html';
    }
});
