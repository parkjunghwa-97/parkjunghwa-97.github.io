from pathlib import Path
import json
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Strengthen SEO / social preview metadata.
SITE_URL = 'https://parkjunghwa-97.github.io/'
LOGO_URL = 'https://parkjunghwa-97.github.io/logo.png'
TITLE = '대한청소만세 | 인천·부평 입주청소 이사청소 특수청소'
DESC = '인천 부평 기반 청소업체 대한청소만세. 입주청소, 이사청소, 사무실·상가청소, 쓰레기집청소, 유품정리, 고독사청소, 비둘기퇴치 상담. 사진 확인 후 작업 범위와 추가비 가능성을 먼저 안내합니다.'
KEYWORDS = '인천 입주청소, 부평 입주청소, 인천 이사청소, 부평 이사청소, 인천 청소업체, 부평 청소업체, 인천 특수청소, 인천 유품정리, 인천 고독사청소, 인천 쓰레기집청소, 인천 비둘기퇴치, 인천 폐기물 처리, 서울 입주청소, 경기 입주청소, 기프트클린, 대한청소만세, 기프트클린 대한청소만세'


def replace_or_add_meta(html, selector, tag):
    # selector examples: name="description", property="og:title"
    pattern = r'<meta\s+[^>]*' + re.escape(selector) + r'[^>]*>'
    if re.search(pattern, html, flags=re.I):
        return re.sub(pattern, tag, html, count=1, flags=re.I)
    return html.replace('<link rel="canonical"', tag + '\n  <link rel="canonical"', 1)

s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S | re.I)
s = replace_or_add_meta(s, 'name="description"', f'<meta name="description" content="{DESC}">')
s = replace_or_add_meta(s, 'name="keywords"', f'<meta name="keywords" content="{KEYWORDS}">')
s = replace_or_add_meta(s, 'name="author"', '<meta name="author" content="기프트클린 대한청소만세">')
s = replace_or_add_meta(s, 'name="robots"', '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">')
s = replace_or_add_meta(s, 'name="format-detection"', '<meta name="format-detection" content="telephone=yes,address=yes,email=no">')

geo_metas = '''  <meta name="geo.region" content="KR-28">
  <meta name="geo.placename" content="인천광역시 부평구">
  <meta name="business:contact_data:locality" content="부평구">
  <meta name="business:contact_data:region" content="인천광역시">
  <meta name="business:contact_data:country_name" content="대한민국">'''
if 'name="geo.region"' not in s:
    s = s.replace('<link rel="canonical"', geo_metas + '\n  <link rel="canonical"', 1)

s = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>', f'<link rel="canonical" href="{SITE_URL}">', s, count=1, flags=re.I)
s = re.sub(r'<link\s+rel="sitemap"[^>]*>', f'<link rel="sitemap" type="application/xml" href="{SITE_URL}sitemap.xml">', s, count=1, flags=re.I)

s = replace_or_add_meta(s, 'property="og:type"', '<meta property="og:type" content="website">')
s = replace_or_add_meta(s, 'property="og:locale"', '<meta property="og:locale" content="ko_KR">')
s = replace_or_add_meta(s, 'property="og:site_name"', '<meta property="og:site_name" content="기프트클린 대한청소만세">')
s = replace_or_add_meta(s, 'property="og:title"', f'<meta property="og:title" content="{TITLE}">')
s = replace_or_add_meta(s, 'property="og:description"', f'<meta property="og:description" content="{DESC}">')
s = replace_or_add_meta(s, 'property="og:url"', f'<meta property="og:url" content="{SITE_URL}">')
s = replace_or_add_meta(s, 'property="og:image"', f'<meta property="og:image" content="{LOGO_URL}">')
if 'property="og:image:alt"' not in s:
    s = s.replace(f'<meta property="og:image" content="{LOGO_URL}">', f'<meta property="og:image" content="{LOGO_URL}">\n  <meta property="og:image:alt" content="기프트클린 대한청소만세 로고">\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">', 1)

s = replace_or_add_meta(s, 'name="twitter:card"', '<meta name="twitter:card" content="summary_large_image">')
s = replace_or_add_meta(s, 'name="twitter:title"', f'<meta name="twitter:title" content="{TITLE}">')
s = replace_or_add_meta(s, 'name="twitter:description"', f'<meta name="twitter:description" content="{DESC}">')
s = replace_or_add_meta(s, 'name="twitter:image"', f'<meta name="twitter:image" content="{LOGO_URL}">')
s = replace_or_add_meta(s, 'name="theme-color"', '<meta name="theme-color" content="#0f172a">')

schema = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": SITE_URL + "#business",
      "name": "기프트클린 대한청소만세",
      "alternateName": ["대한청소만세", "기프트클린"],
      "url": SITE_URL,
      "telephone": "+82-10-4122-9207",
      "image": LOGO_URL,
      "logo": LOGO_URL,
      "priceRange": "사진 확인 및 현장 상태에 따라 상담 후 안내",
      "description": "인천 부평 기반 청소업체. 입주청소, 이사청소, 사무실·상가청소, 쓰레기집청소, 특수청소, 유품정리, 고독사청소, 폐기물 처리, 비둘기 퇴치 상담.",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "부영로 165",
        "addressLocality": "부평구",
        "addressRegion": "인천광역시",
        "addressCountry": "KR"
      },
      "areaServed": ["인천", "부평", "계양", "서구", "남동구", "연수구", "송도", "청라", "검단", "서울", "경기", "전국 특수청소 상담"],
      "serviceArea": ["인천", "서울", "경기", "전국 출장 상담 가능 서비스"],
      "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "00:00",
        "closes": "23:59"
      }],
      "contactPoint": [{
        "@type": "ContactPoint",
        "telephone": "+82-10-4122-9207",
        "contactType": "customer service",
        "areaServed": "KR",
        "availableLanguage": "Korean"
      }],
      "sameAs": [
        "https://pf.kakao.com/_lxhwGX",
        "https://m.blog.naver.com/krcleangod?tab=1",
        "https://www.instagram.com/gift.clean"
      ],
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "대한청소만세 청소 서비스",
        "itemListElement": [
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "입주청소"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "이사청소"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "사무실·상가청소"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "쓰레기집청소"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "유품정리"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "고독사청소"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "비둘기퇴치"}},
          {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "폐기물 처리"}}
        ]
      }
    },
    {
      "@type": "WebSite",
      "@id": SITE_URL + "#website",
      "url": SITE_URL,
      "name": "기프트클린 대한청소만세",
      "publisher": {"@id": SITE_URL + "#business"}
    },
    {
      "@type": "FAQPage",
      "@id": SITE_URL + "#faq",
      "mainEntity": [
        {"@type":"Question","name":"사진만 보내도 견적 가능한가요?","acceptedAnswer":{"@type":"Answer","text":"현장 사진이나 영상을 보내주시면 오염도, 짐 유무, 폐기물 양, 작업 범위를 확인해 예상 견적을 안내드립니다. 사진에 보이지 않는 오염이나 추가 작업이 있는 경우 현장에서 금액이 변동될 수 있습니다."}},
        {"@type":"Question","name":"입주청소와 이사청소는 다른가요?","acceptedAnswer":{"@type":"Answer","text":"입주청소는 새로 들어가기 전 빈 공간을 기준으로 진행하는 경우가 많고, 이사청소는 이전 거주 흔적이나 생활 오염이 남아 있는 경우가 많습니다. 현장 상태에 따라 작업 범위와 비용이 달라질 수 있습니다."}},
        {"@type":"Question","name":"추가 비용은 언제 발생하나요?","acceptedAnswer":{"@type":"Answer","text":"상담 당시 확인되지 않은 심한 오염, 폐기물 증가, 추가 공간, 추가 작업 요청, 장비 사용, 유료 주차비 등이 있는 경우 추가 비용이 발생할 수 있습니다. 추가 작업은 사전 안내 후 진행됩니다."}},
        {"@type":"Question","name":"비둘기 퇴치는 어떤 작업을 하나요?","acceptedAnswer":{"@type":"Answer","text":"현장 상태에 따라 분변 제거, 둥지 제거, 알·새끼 확인, 유입경로 차단막 설치 등을 진행합니다. 스카이 장비나 외부 작업이 필요한 경우 별도 안내드립니다."}}
      ]
    }
  ]
}
jsonld = '  <!-- SCHEMA_ORG_JSONLD -->\n  <script type="application/ld+json">\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n</script>'
s = re.sub(r'\s*<!-- SCHEMA_ORG_JSONLD -->\s*<script type="application/ld\+json">.*?</script>', '\n' + jsonld, s, count=1, flags=re.S)

# Add cost guide navigation and section.
if "showPage('price')" not in s:
    s = s.replace(
        "      <button class=\"nav-btn\" onclick=\"showPage('service')\">서비스안내</button>\n      <button class=\"nav-btn\" onclick=\"showPage('portfolio')\">작업사례</button>",
        "      <button class=\"nav-btn\" onclick=\"showPage('service')\">서비스안내</button>\n      <button class=\"nav-btn\" onclick=\"showPage('price')\">비용안내</button>\n      <button class=\"nav-btn\" onclick=\"showPage('portfolio')\">작업사례</button>"
    )

price_css = '''

    /* PRICE_GUIDE_SECTION */
    .price-page{background:#f8fafc}
    .price-lead{max-width:760px}
    .price-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:24px}
    .price-card{background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08)}
    .price-card h3{margin:0 0 14px;font-size:20px;color:#0f172a;letter-spacing:-.03em}
    .price-row{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;padding:10px 0;border-bottom:1px solid #eef2f7;color:#334155;font-size:15px;line-height:1.45}
    .price-row:last-child{border-bottom:0}
    .price-row span:last-child{font-weight:900;color:#0f172a;white-space:nowrap}
    .price-note{margin-top:24px;background:#0f172a;color:#fff;border-radius:24px;padding:24px;line-height:1.8;font-weight:750}
    .price-note p{margin:0 0 8px}
    .price-note p:last-child{margin-bottom:0}
    .price-cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}
    .price-cta button,.price-cta a{border:0;border-radius:999px;padding:14px 20px;background:#051231;color:#fff;font-weight:900;cursor:pointer;box-shadow:0 10px 24px rgba(15,23,42,.18)}
    .price-cta a{display:inline-flex;align-items:center;justify-content:center;background:#fff;color:#0f172a;border:1px solid #cbd5e1}
    @media(max-width:760px){.nav-menu{grid-template-columns:repeat(3,1fr)}.price-card{border-radius:18px;padding:18px}.price-row{font-size:14.5px}.price-note{border-radius:20px;padding:20px}.price-cta{display:grid}.price-cta button,.price-cta a{width:100%}}
'''
if '/* PRICE_GUIDE_SECTION */' not in s:
    s = s.replace('</style>', price_css + '\n</style>', 1)

price_section = '''

  <section id="price" class="page price-page">
    <div class="page-inner">
      <h2>비용안내</h2>
      <p class="sub price-lead">아래 금액은 상담 전 기준을 잡기 위한 시작가입니다. 실제 비용은 평수, 오염도, 짐 유무, 폐기물 양, 추가 작업 여부에 따라 달라질 수 있습니다.</p>

      <div class="price-grid">
        <div class="price-card">
          <h3>입주 · 이사청소</h3>
          <div class="price-row"><span>원룸</span><span>180,000원~</span></div>
          <div class="price-row"><span>1.5룸</span><span>220,000원~</span></div>
          <div class="price-row"><span>투룸</span><span>240,000원~</span></div>
          <div class="price-row"><span>쓰리룸</span><span>280,000원~</span></div>
          <div class="price-row"><span>26평 이상</span><span>평당 10,000원~</span></div>
        </div>

        <div class="price-card">
          <h3>쓰레기집 청소</h3>
          <div class="price-row"><span>원룸 1겹</span><span>500,000원~</span></div>
          <div class="price-row"><span>원룸 디테일</span><span>700,000원~</span></div>
          <div class="price-row"><span>투룸 1겹</span><span>700,000원~</span></div>
          <div class="price-row"><span>투룸 디테일</span><span>900,000원~</span></div>
          <div class="price-row"><span>쓰리룸 이상</span><span>방문견적</span></div>
        </div>

        <div class="price-card">
          <h3>비둘기 퇴치</h3>
          <div class="price-row"><span>분변 제거만</span><span>150,000원~</span></div>
          <div class="price-row"><span>둥지·알·새끼·분변 제거<br>유입경로 차단막 설치 포함</span><span>250,000원~</span></div>
          <div class="price-row"><span>스카이 장비 필요 시</span><span>별도 안내</span></div>
        </div>

        <div class="price-card">
          <h3>고독사 특수청소</h3>
          <div class="price-row"><span>고인 발견 장소 처리</span><span>1,500,000원~</span></div>
          <div class="price-row"><span>추가 공간 처리</span><span>2,000,000원~ 협의</span></div>
          <div class="price-row"><span>오염 범위·악취·폐기물</span><span>확인 후 안내</span></div>
        </div>
      </div>

      <div class="price-note">
        <p>※ 현장 상황 및 오염도에 따라 비용이 변동될 수 있습니다.</p>
        <p>※ 추가 작업 발생 시 사전 안내 후 진행됩니다.</p>
        <p>※ 사진이나 영상을 보내주시면 예상 견적 안내가 가능합니다.</p>
      </div>

      <div class="price-cta">
        <button type="button" onclick="showPage('contact')">내 현장 견적 문의하기</button>
        <a href="https://pf.kakao.com/_lxhwGX" target="_blank">카카오톡으로 사진 보내기</a>
      </div>
    </div>
  </section>
'''
if 'id="price"' not in s:
    s = s.replace('\n  <section id="portfolio" class="page">', price_section + '\n  <section id="portfolio" class="page">', 1)

# Keep slider moving while draggable.
s = s.replace("if(track){track.style.animation='none';}", "if(track){track.style.animationPlayState='running';}")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")

# Match company-intro animation feel on mobile and desktop.
s = s.replace("const startTop=isMobile ? '38vh' : '50vh';", "const startTop=isMobile ? '43vh' : '50vh';")
s = s.replace("const startTop=isMobile ? '45vh' : '50vh';", "const startTop=isMobile ? '43vh' : '50vh';")
s = s.replace("const startTop=isMobile ? '39vh' : '50vh';", "const startTop=isMobile ? '43vh' : '50vh';")
s = s.replace("const startFont=isMobile ? '36px' : '80px';", "const startFont=isMobile ? '37px' : '80px';")
s = s.replace("const startFont=isMobile ? '38px' : '80px';", "const startFont=isMobile ? '37px' : '80px';")
s = s.replace("const duration=isMobile ? 3200 : 950;", "const duration=isMobile ? 1750 : 950;")
s = s.replace("const duration=isMobile ? 1500 : 950;", "const duration=isMobile ? 1750 : 950;")
s = s.replace("const duration=isMobile ? 1250 : 950;", "const duration=isMobile ? 1750 : 950;")
s = s.replace("offset:.18", "offset:.24")
s = s.replace("transform:'translate(-50%,-50%) scale(.98)',opacity:1,offset:.72", "transform:'translate(-50%,-50%) scale(.94)',opacity:1,offset:.58")
s = s.replace("transform:'translate(-50%,-50%) scale(.92)',opacity:1,offset:.60", "transform:'translate(-50%,-50%) scale(.94)',opacity:1,offset:.58")
s = s.replace("setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 450 : 40);", "setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 260 : 40);")
s = s.replace("setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);", "setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 260 : 40);")

# Keep the flying text visible above floating contact buttons.
css_about = '''

    /* MOBILE_ABOUT_ACTION_VISIBILITY */
    @media(max-width:760px){
      .fly-about-text{z-index:2147483646!important;color:#0f172a!important;text-shadow:0 10px 30px rgba(255,255,255,.98),0 2px 10px rgba(255,255,255,.96)!important}
    }
'''
if '/* MOBILE_ABOUT_ACTION_VISIBILITY */' not in s:
    s = s.replace('</style>', css_about + '\n</style>', 1)

# Strong lightbox CSS, independent from the older one.
css = '''

    /* UNIVERSAL_SLIDER_ZOOM */
    .universal-slider-lightbox{position:fixed!important;inset:0!important;background:rgba(15,23,42,.92)!important;z-index:2147483647!important;display:none;align-items:center;justify-content:center;padding:18px}
    .universal-slider-lightbox.open{display:flex!important}
    .universal-slider-lightbox img{max-width:94vw;max-height:88vh;object-fit:contain;background:#fff;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.42)}
    .universal-slider-lightbox button{position:fixed;top:14px;right:14px;border:0;background:#fff;color:#0f172a;border-radius:999px;width:42px;height:42px;font-size:24px;font-weight:900;cursor:pointer}
    .review-marquee img,.cert-marquee img,.case-row img{cursor:zoom-in!important}
'''
if '/* UNIVERSAL_SLIDER_ZOOM */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

# Capture pointer events before the drag code can swallow the click.
js = r'''

    /* UNIVERSAL_SLIDER_ZOOM */
    (function(){
      var selector='.review-marquee img,.cert-marquee img,.case-row img';
      var down=null;
      var lastOpen=0;
      function getImg(e){
        return e && e.target && e.target.closest ? e.target.closest(selector) : null;
      }
      function box(){
        var el=document.querySelector('.universal-slider-lightbox');
        if(el){return el;}
        el=document.createElement('div');
        el.className='universal-slider-lightbox';
        el.innerHTML='<button type="button" aria-label="닫기">×</button><img alt="확대 이미지">';
        document.body.appendChild(el);
        el.addEventListener('click',function(e){if(e.target===el || e.target.tagName==='BUTTON'){el.classList.remove('open');}},true);
        document.addEventListener('keydown',function(e){if(e.key==='Escape'){el.classList.remove('open');}},true);
        return el;
      }
      function openImg(img){
        if(!img){return;}
        var now=Date.now();
        if(now-lastOpen<280){return;}
        lastOpen=now;
        var el=box();
        el.querySelector('img').src=img.currentSrc || img.src;
        el.classList.add('open');
      }
      document.addEventListener('pointerdown',function(e){
        var img=getImg(e);
        if(img){down={img:img,x:e.clientX,y:e.clientY};}
      },true);
      document.addEventListener('pointerup',function(e){
        if(!down){return;}
        var img=getImg(e) || down.img;
        var dx=Math.abs((e.clientX||0)-down.x);
        var dy=Math.abs((e.clientY||0)-down.y);
        var same=img===down.img;
        var smallMove=dx<9 && dy<9;
        down=null;
        if(same && smallMove){
          e.preventDefault();
          e.stopPropagation();
          openImg(img);
        }
      },true);
      document.addEventListener('click',function(e){
        var img=getImg(e);
        if(img){
          e.preventDefault();
          e.stopPropagation();
          openImg(img);
        }
      },true);
    })();
'''
if '/* UNIVERSAL_SLIDER_ZOOM */' not in s.split('</script>')[-2]:
    pos=s.rfind('</script>')
    if pos!=-1:
        s=s[:pos]+js+s[pos:]

p.write_text(s, encoding='utf-8')