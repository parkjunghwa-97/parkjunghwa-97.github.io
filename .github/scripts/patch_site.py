from pathlib import Path
from datetime import date
import json
import re

index = Path("index.html")
text = index.read_text(encoding="utf-8")

# 1) SEO meta tags
seo_title = "기프트클린 대한청소만세 | 대전 청소업체 · 입주청소 · 특수청소 · 유품정리"
seo_description = "기프트클린 대한청소만세는 대전·세종·충청권 중심의 청소업체입니다. 입주청소, 이사청소, 사무실·상가청소, 쓰레기집 청소, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치 상담을 진행합니다."

seo_block = f'''  <title>{seo_title}</title>
  <!-- SEO_OPTIMIZED_BY_CHATGPT -->
  <meta name="description" content="{seo_description}">
  <meta name="keywords" content="대전 청소업체, 세종 청소업체, 충청권 청소업체, 입주청소, 이사청소, 사무실청소, 상가청소, 쓰레기집 청소, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치, 기프트클린, 대한청소만세">
  <meta name="author" content="기프트클린 대한청소만세">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="naver-site-verification" content="">
  <meta name="google-site-verification" content="">
  <meta name="format-detection" content="telephone=yes">
  <meta name="geo.region" content="KR-30">
  <meta name="geo.placename" content="대전광역시">
  <link rel="canonical" href="https://parkjunghwa-97.github.io/">
  <link rel="sitemap" type="application/xml" href="https://parkjunghwa-97.github.io/sitemap.xml">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="ko_KR">
  <meta property="og:site_name" content="기프트클린 대한청소만세">
  <meta property="og:title" content="{seo_title}">
  <meta property="og:description" content="{seo_description}">
  <meta property="og:url" content="https://parkjunghwa-97.github.io/">
  <meta property="og:image" content="https://parkjunghwa-97.github.io/logo.png">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{seo_title}">
  <meta name="twitter:description" content="{seo_description}">
  <meta name="twitter:image" content="https://parkjunghwa-97.github.io/logo.png">
  <meta name="theme-color" content="#0f172a">'''

if "SEO_OPTIMIZED_BY_CHATGPT" not in text:
    text = re.sub(r"  <title>.*?</title>", seo_block, text, count=1, flags=re.S)

# 2) Structured data JSON-LD
faq_entities = [
    ("사진만 보내도 견적 가능한가요?", "네, 가능합니다. 현장 사진이나 영상을 보내주시면 오염도, 짐 유무, 폐기물 양, 작업 범위를 확인해 예상 견적을 안내드립니다. 다만 사진에 보이지 않는 오염이나 추가 작업이 있는 경우 현장에서 금액이 변동될 수 있습니다."),
    ("당일 청소도 가능한가요?", "일정이 맞는 경우 당일 작업도 가능합니다. 작업 종류, 현장 상태, 이동 거리, 투입 인원에 따라 가능 여부가 달라질 수 있어 상담 시 확인이 필요합니다."),
    ("입주청소와 이사청소는 다른가요?", "입주청소는 새로 들어가기 전 빈 공간을 기준으로 진행하는 경우가 많고, 이사청소는 이전 거주 흔적이나 생활 오염이 남아 있는 경우가 많습니다. 현장 상태에 따라 작업 범위와 비용이 달라질 수 있습니다."),
    ("쓰레기집 청소도 가능한가요?", "네, 가능합니다. 생활쓰레기, 음식물 쓰레기, 악취, 바닥 오염, 폐기물 양을 확인한 뒤 작업 범위와 예상 비용을 안내드립니다. 사진 확인 후 예상 견적 안내가 가능합니다."),
    ("비둘기 퇴치는 어떤 작업을 하나요?", "현장 상태에 따라 분변 제거, 둥지 제거, 알·새끼 확인, 유입경로 차단막 설치 등을 진행합니다. 스카이 장비나 외부 작업이 필요한 경우 별도 안내드립니다."),
    ("추가 비용은 언제 발생하나요?", "상담 당시 확인되지 않은 심한 오염, 폐기물 증가, 추가 공간, 추가 작업 요청, 장비 사용, 유료 주차비 등이 있는 경우 추가 비용이 발생할 수 있습니다. 추가 작업은 사전 안내 후 진행됩니다."),
    ("작업 후 A/S는 가능한가요?", "작업 완료 후 3일 이내 접수 가능합니다. 사진 또는 영상으로 확인 후 작업 범위 내 미흡한 부분인지 확인하여 안내드립니다. 작업 완료 후 새로 발생한 오염이나 사용 중 발생한 오염은 A/S 대상에서 제외될 수 있습니다.")
]

structured_data = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": "https://parkjunghwa-97.github.io/#website",
            "url": "https://parkjunghwa-97.github.io/",
            "name": "기프트클린 대한청소만세",
            "inLanguage": "ko-KR",
            "description": seo_description
        },
        {
            "@type": ["LocalBusiness", "HomeAndConstructionBusiness"],
            "@id": "https://parkjunghwa-97.github.io/#business",
            "name": "기프트클린 대한청소만세",
            "alternateName": ["대한청소만세", "GiftClean"],
            "url": "https://parkjunghwa-97.github.io/",
            "logo": "https://parkjunghwa-97.github.io/logo.png",
            "image": "https://parkjunghwa-97.github.io/logo.png",
            "telephone": "+82-10-4122-9207",
            "priceRange": "상담 후 안내",
            "description": seo_description,
            "areaServed": [
                {"@type": "City", "name": "대전광역시"},
                {"@type": "City", "name": "세종특별자치시"},
                {"@type": "AdministrativeArea", "name": "충청권"},
                {"@type": "Country", "name": "대한민국"}
            ],
            "availableLanguage": ["ko-KR"],
            "sameAs": [
                "https://m.blog.naver.com/krcleangod?tab=1",
                "https://www.instagram.com/gift.clean"
            ],
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+82-10-4122-9207",
                "contactType": "customer service",
                "areaServed": "KR",
                "availableLanguage": "ko-KR"
            },
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "청소 서비스",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "입주청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "이사청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "사무실·상가청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "쓰레기집 청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "특수청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "고독사 특수청소"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "유품정리"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "폐기물 처리"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "비둘기 퇴치"}}
                ]
            }
        },
        {
            "@type": "FAQPage",
            "@id": "https://parkjunghwa-97.github.io/#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}
                } for q, a in faq_entities
            ]
        }
    ]
}

json_ld = '<script type="application/ld+json">\n' + json.dumps(structured_data, ensure_ascii=False, indent=2) + '\n  </script>'
if "parkjunghwa-97.github.io/#business" not in text:
    text = text.replace("  </style>\n</head>", "  </style>\n\n  " + json_ld.replace("\n", "\n  ") + "\n</head>", 1)

# 3) CSS for review slider + FAQ cards + more info area
site_css = '''
    /* 고객 후기 자동 슬라이드 + FAQ + SEO 보강 */
    .review-sub{margin-top:-4px;margin-bottom:18px;color:#64748b;line-height:1.7}
    .review-marquee{width:100%;overflow:hidden;position:relative;margin-top:8px;padding:8px 0 20px}
    .review-marquee:before,.review-marquee:after{content:"";position:absolute;top:0;width:46px;height:100%;z-index:2;pointer-events:none}
    .review-marquee:before{left:0;background:linear-gradient(to right,#f8fafc,rgba(248,250,252,0))}
    .review-marquee:after{right:0;background:linear-gradient(to left,#f8fafc,rgba(248,250,252,0))}
    .review-track{display:flex;align-items:flex-start;gap:18px;width:max-content;animation:reviewMove 58s linear infinite}
    .review-marquee:hover .review-track{animation-play-state:paused}
    .review-shot{flex:0 0 auto;background:#fff;border-radius:22px;padding:12px;box-shadow:0 8px 24px rgba(15,23,42,.10)}
    .review-shot img{display:block;height:520px;width:auto;max-width:none;object-fit:contain;border-radius:16px}
    @keyframes reviewMove{from{transform:translateX(0)}to{transform:translateX(-50%)}}
    .faq-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:24px 0 30px}
    .faq-card{background:#fff;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);border:1px solid rgba(226,232,240,.9)}
    .faq-card b{display:block;font-size:17px;color:#0f172a;margin-bottom:10px;line-height:1.45}
    .faq-card p{margin:0;color:#64748b;line-height:1.7;font-size:15px}
    .more-info{margin-top:30px;background:#fff;border-radius:24px;box-shadow:0 10px 28px rgba(15,23,42,.09);overflow:hidden}
    .more-info>summary{background:#0f172a;color:#fff;font-size:18px;padding:20px 22px}
    .more-info-intro{padding:18px 22px 0;margin:0;color:#64748b;line-height:1.7}
    .more-info .accordion{padding:18px 18px 22px}
    @media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}
    @media(max-width:430px){.review-shot img{height:390px}}
'''
if "고객 후기 자동 슬라이드 + FAQ + SEO 보강" not in text:
    text = text.replace("  </style>", site_css + "\n  </style>", 1)

# 4) Navigation label: 확인사항 -> FAQ
text = text.replace('>확인사항</button>', '>FAQ</button>')

# 5) Portfolio review slider
old_review = '''<h3 class="review-title">고객 후기</h3>

<div class="review-grid">
  <div class="review-card review-image-card">
    <img src="review1.jpg" alt="고객 후기 1">
  </div>

  <div class="review-card review-image-card">
    <img src="review2.jpg" alt="고객 후기 2">
  </div>

  <div class="review-card review-image-card">
    <img src="review3.jpg" alt="고객 후기 3">
  </div>
</div>'''
review_items = "\n".join(
    f'          <div class="review-shot"><img src="images/reviews/review-{i:02d}.jpg" alt="고객 후기 {i}"></div>'
    for i in range(1, 9)
)
new_review = f'''<h3 class="review-title">고객 후기</h3>
<p class="sub review-sub">실제 고객님들이 남겨주신 후기입니다.</p>

<div class="review-marquee" aria-label="고객 후기 자동 슬라이드">
  <div class="review-track">
{review_items}

{review_items}
  </div>
</div>'''
if "images/reviews/review-01.jpg" not in text and old_review in text:
    text = text.replace(old_review, new_review, 1)

# 6) FAQ visible cards and move existing policy details under more info
faq_cards = "\n".join(
    f'''        <div class="faq-card"><b>{q}</b><p>{a}</p></div>'''
    for q, a in faq_entities
)
new_policy_header = f'''      <h2>자주 묻는 질문</h2>
      <p class="sub">상담 전 많이 물어보시는 내용을 먼저 정리했습니다.</p>
      <div class="faq-grid">
{faq_cards}
      </div>

      <details class="more-info">
        <summary>더 자세한 안내사항 보기</summary>
        <p class="more-info-intro">예약, 환불, 추가비용, A/S, 면책사항 등 작업 전 확인이 필요한 내용을 정리했습니다.</p>
        <div class="accordion">'''

if '<h2>작업 전 확인사항</h2>' in text:
    text = text.replace('      <h2>작업 전 확인사항</h2>\n      <p class="sub">작업 전 꼭 확인해 주세요. 각 항목을 누르면 자세한 내용이 펼쳐집니다.</p>\n      <div class="accordion">', new_policy_header, 1)
    text = text.replace('      </div>\n    </div>\n  </section>\n\n  <section id="contact" class="page">', '        </div>\n      </details>\n    </div>\n  </section>\n\n  <section id="contact" class="page">', 1)

# 7) sitemap / robots / llms
today = date.today().isoformat()
Path("sitemap.xml").write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://parkjunghwa-97.github.io/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
''', encoding="utf-8")

Path("robots.txt").write_text('''User-agent: *
Allow: /

Sitemap: https://parkjunghwa-97.github.io/sitemap.xml
''', encoding="utf-8")

Path("llms.txt").write_text('''# 기프트클린 대한청소만세

기프트클린 대한청소만세는 대전·세종·충청권 중심의 청소업체입니다.

## 주요 서비스
- 입주청소
- 이사청소
- 사무실·상가청소
- 쓰레기집 청소
- 특수청소
- 고독사 특수청소
- 유품정리
- 폐기물 처리
- 비둘기 퇴치

## 상담
전화: 010-4122-9207
공식 홈페이지: https://parkjunghwa-97.github.io/
네이버 블로그: https://m.blog.naver.com/krcleangod?tab=1
인스타그램: https://www.instagram.com/gift.clean
''', encoding="utf-8")

# 8) Remove temporary / broken workflow files after successful patch
for p in [
    Path(".chatgpt-write-test.txt"),
    Path(".chatgpt-review-trigger.txt"),
    Path(".github/workflows/add-review-slider.yml"),
    Path(".github/scripts/patch_site.py")
]:
    if p.exists():
        p.unlink()

index.write_text(text, encoding="utf-8")
