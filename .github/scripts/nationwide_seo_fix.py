from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Existing Korean copy cleanups kept idempotent.
s = s.replace('현장일지', '현장기록')
s = s.replace('작업사례 템플릿 보기', '현장기록 보기')
s = s.replace('<p class="sub">실제 현장별 작업 내용과 정보성 콘텐츠를 지역, 서비스, 작업 범위 중심으로 정리하는 공간입니다.</p>', '')
s = s.replace('<a href="/cases/">체크리스트 보기</a>', '<p>입주 전 확인 기준을 항목별로 정리하는 정보형 글입니다.</p>')
s = s.replace('<a href="/cases/">사진상담 기준 보기</a>', '<p>사진상담 전에 필요한 사진 기준을 정리하는 글입니다.</p>')
s = s.replace('<a href="/cases/">현장기록 보기</a>', '<p>실제 현장 기준으로 작업 범위를 정리하는 글입니다.</p>')

# Reposition the site from an move-in cleaning homepage to a special-cleaning first homepage.
seo_replacements = [
    ('<title>대한청소만세 | 인천·부평 입주청소 이사청소 특수청소</title>', '<title>대한청소만세 | 특수청소 쓰레기집청소 유품정리 비둘기퇴치</title>'),
    ('<meta name="description" content="서울·경기·인천 입주청소, 이사청소, 특수청소, 유품정리, 비둘기퇴치 비용 안내.">', '<meta name="description" content="특수청소 중심 청소업체. 쓰레기집 청소, 유품정리, 비둘기 배설물 청소, 악취 제거, 폐기물 처리, 입주·이사청소 상담.">'),
    ('<meta property="og:title" content="대한청소만세 | 인천·부평 입주청소 이사청소 특수청소">', '<meta property="og:title" content="대한청소만세 | 특수청소 쓰레기집청소 유품정리 비둘기퇴치">'),
    ('<meta property="og:description" content="서울·경기·인천 입주청소, 이사청소, 특수청소, 유품정리, 비둘기퇴치 비용 안내.">', '<meta property="og:description" content="특수청소 중심 청소업체. 쓰레기집 청소, 유품정리, 비둘기 배설물 청소, 악취 제거, 폐기물 처리, 입주·이사청소 상담.">'),
    ('<meta name="twitter:title" content="대한청소만세 | 인천·부평 입주청소 이사청소 특수청소">', '<meta name="twitter:title" content="대한청소만세 | 특수청소 쓰레기집청소 유품정리 비둘기퇴치">'),
    ('<meta name="twitter:description" content="서울·경기·인천 입주청소, 이사청소, 특수청소, 유품정리, 비둘기퇴치 비용 안내.">', '<meta name="twitter:description" content="특수청소 중심 청소업체. 쓰레기집 청소, 유품정리, 비둘기 배설물 청소, 악취 제거, 폐기물 처리, 입주·이사청소 상담.">'),
    ('"description": "인천 부평 기반 청소업체. 입주청소, 이사청소, 사무실·상가청소, 쓰레기집청소, 특수청소, 유품정리, 고독사청소, 폐기물 처리, 비둘기 퇴치 상담."', '"description": "특수청소 중심 청소업체. 쓰레기집청소, 유품정리, 고독사청소, 비둘기 배설물 청소, 악취 제거, 폐기물 처리, 화재 오염 상담과 입주·이사청소를 상담합니다."'),
    ('"priceRange": "사진 확인 및 현장 상태에 따라 상담 후 안내"', '"priceRange": "현장 사진과 오염 범위 확인 후 안내"'),
]
for old, new in seo_replacements:
    s = s.replace(old, new)

hero_old = '''<div class="hero-main">낮은 견적보다 중요한 건,<br>불안하지 않은 과정입니다.</div>

      <div class="hero-sub">사진 상담으로 현장 상태를 먼저 확인하고<br>작업 범위와 추가 비용 가능성을 안내합니다.<br><br>서울·경기·인천 입주청소 · 이사청소<br>전국 특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소</div>

      <div class="hero-cta">
        <button class="hero-btn" onclick="showPage('contact')">내 상황 상담받기</button>
        <button class="hero-btn secondary" onclick="showPage('portfolio')">작업사례 보기</button>
      </div>

      <div class="hero-proof">동의 없는 추가 작업은 진행하지 않습니다.</div>'''
hero_new = '''<h1 class="hero-main">특수청소가 필요한 현장은<br>일반 청소 기준으로 판단하지 않습니다.</h1>

      <div class="hero-sub">쓰레기집 청소, 유품정리, 비둘기 배설물 청소,<br>악취 제거, 폐기물 처리처럼 현장 상태가 먼저인 작업을 상담합니다.<br><br>입주청소 · 이사청소도 가능하지만,<br>대한청소만세의 중심은 특수현장 판단입니다.</div>

      <div class="hero-cta">
        <button class="hero-btn" onclick="showPage('contact')">특수청소 상담하기</button>
        <button class="hero-btn secondary" onclick="showPage('service')">입주·이사청소도 보기</button>
      </div>

      <div class="hero-proof">사진과 현장 상태를 확인한 뒤 작업 범위와 추가 비용 가능성을 먼저 안내합니다.</div>'''
s = s.replace(hero_old, hero_new)

about_old = '대한청소만세는 입주청소, 이사청소, 사무실·상가청소, 쓰레기집 정리, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치 등 다양한 현장 서비스를 제공하고 있습니다.'
about_new = '대한청소만세는 쓰레기집 정리, 유품정리, 고독사 특수청소, 비둘기 배설물 청소, 폐기물 처리처럼 일반 청소 기준으로 판단하기 어려운 특수현장을 중심으로 상담합니다. 입주청소, 이사청소, 사무실·상가청소도 함께 진행합니다.'
s = s.replace(about_old, about_new)

service_old = '''<h2>서비스 안내</h2>
      <p class="sub">서울·경기·인천 등 수도권 입주청소 · 이사청소

특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소 · 폐기물 처리 · 비둘기 퇴치<br>전국 출장 상담 가능.

사진 상담으로 현장 상태를 먼저 확인하고,<br>작업 범위와 예상 견적을 안내해드립니다.</p>
<div class="trust-box">
        <b>낮은 견적보다 중요한 건,<br>작업 전 정확한 안내입니다.</b>
        <p>현장에서 금액이 달라질 수 있는 부분,<br>추가 작업이 필요한 상황을 먼저 설명합니다.</p>
        <p class="trust-note">동의 없는 추가 작업은 진행하지 않습니다.</p>
      </div>

      <div class="grid">
        <div class="card"><b>🏠 입주 · 이사청소</b><p>새 공간을 깨끗하게 시작할 수 있도록 보이지 않는 곳까지 정리합니다.</p></div>
        <div class="card"><b>🏢 사무실 · 상가청소</b><p>업무공간과 영업공간의 상태에 맞춰 청소 범위를 안내합니다.</p></div>
        <div class="card"><b>🗑 쓰레기집 정리</b><p>폐기물 양과 오염 상태를 확인한 뒤 필요한 인원과 작업을 산정합니다.</p></div>
        <div class="card"><b>🧹 특수청소</b><p>일반 청소로 해결하기 어려운 오염 현장을 상황에 맞게 처리합니다.</p></div>
        <div class="card"><b>🫧 고독사 특수청소</b><p>고인 발견 장소 처리 및 특수 오염 제거 작업을 진행합니다.</p></div>
        <div class="card"><b>🤍 유품정리</b><p>남겨진 공간을 조심스럽고 차분하게 정리합니다.</p></div>
        <div class="card"><b>🚛 폐기물 처리</b><p>현장 폐기물 양에 따라 수거와 정리 범위를 안내합니다.</p></div>
        <div class="card"><b>🕊 비둘기 퇴치</b><p>분변 제거, 둥지 제거, 유입경로 차단 작업을 진행합니다.</p></div>
      </div>'''
service_new = '''<h2>특수청소 중심 서비스 안내</h2>
      <p class="sub">특수청소는 현장마다 오염 원인, 폐기물 양, 냄새, 출입 조건이 다릅니다.<br>대한청소만세는 사진과 영상을 먼저 확인하고 작업 범위, 추가 비용 가능성, 준비사항을 안내합니다.<br><br>입주청소와 이사청소도 상담하지만, 홈페이지의 중심은 쓰레기집 청소 · 유품정리 · 비둘기 배설물 청소 · 폐기물 처리 같은 특수현장입니다.</p>
<div class="trust-box">
        <b>특수현장은 가격보다<br>작업 범위 확인이 먼저입니다.</b>
        <p>오염 범위, 악취, 폐기물, 출입 조건을 확인한 뒤<br>가능한 작업과 어려운 부분을 먼저 설명합니다.</p>
        <p class="trust-note">동의 없는 추가 작업은 진행하지 않습니다.</p>
      </div>

      <div class="grid">
        <div class="card"><b>🧹 특수청소</b><p>일반 청소로 끝나기 어려운 오염, 악취, 폐기물 현장을 먼저 확인합니다.</p></div>
        <div class="card"><b>🗑 쓰레기집 청소</b><p>폐기물 양, 바닥 오염, 악취 상태를 보고 작업 인원과 범위를 산정합니다.</p></div>
        <div class="card"><b>🤍 유품정리</b><p>남겨진 물품과 공간 상태를 확인하고 조심스럽게 정리 범위를 안내합니다.</p></div>
        <div class="card"><b>🫧 고독사 특수청소</b><p>고인 발견 장소의 오염 범위와 악취, 폐기물 처리 필요 여부를 확인합니다.</p></div>
        <div class="card"><b>🕊 비둘기 퇴치</b><p>비둘기 배설물, 둥지, 유입 경로, 차단 가능 범위를 함께 확인합니다.</p></div>
        <div class="card"><b>🚛 폐기물 처리</b><p>현장 폐기물 종류와 양에 따라 수거와 정리 범위를 안내합니다.</p></div>
        <div class="card"><b>🔥 화재·그을음 오염 상담</b><p>그을음, 냄새, 오염 범위를 확인해 가능한 청소 범위를 안내합니다.</p></div>
        <div class="card"><b>🏠 입주 · 이사청소</b><p>새 공간이나 이사 후 공간도 평수와 오염도에 따라 상담합니다.</p></div>
        <div class="card"><b>🏢 사무실 · 상가청소</b><p>업무공간과 영업공간의 상태에 맞춰 청소 범위를 안내합니다.</p></div>
      </div>'''
s = s.replace(service_old, service_new)

portfolio_old = '''<p class="sub">현장별 작업 사례를 한눈에 확인하실 수 있습니다.</p>

      <div class="case-row">
        <div class="case-strip">
          <div class="case-mini">입주청소 전후사진</div>
          <div class="case-mini">비둘기 퇴치 전후사진</div>
          <div class="case-mini">쓰레기집 정리 전후사진</div>
          <div class="case-mini">특수청소 작업사례</div>
          <div class="case-mini">고독사 특수청소</div>
          <div class="case-mini">유품정리 작업사례</div>
          <div class="case-mini">사무실 · 상가청소</div>

          <div class="case-mini">입주청소 전후사진</div>
          <div class="case-mini">비둘기 퇴치 전후사진</div>
          <div class="case-mini">쓰레기집 정리 전후사진</div>
          <div class="case-mini">특수청소 작업사례</div>
          <div class="case-mini">고독사 특수청소</div>
          <div class="case-mini">유품정리 작업사례</div>
          <div class="case-mini">사무실 · 상가청소</div>
        </div>
      </div>'''
portfolio_new = '''<p class="sub">쓰레기집 청소, 비둘기 퇴치, 유품정리 등 특수현장 사례를 먼저 정리합니다. 입주·이사청소 사례도 함께 확인하실 수 있습니다.</p>

      <div class="case-row">
        <div class="case-strip">
          <div class="case-mini">특수청소 작업사례</div>
          <div class="case-mini">쓰레기집 정리 전후사진</div>
          <div class="case-mini">비둘기 퇴치 전후사진</div>
          <div class="case-mini">유품정리 작업사례</div>
          <div class="case-mini">고독사 특수청소</div>
          <div class="case-mini">폐기물 처리 사례</div>
          <div class="case-mini">입주청소 전후사진</div>
          <div class="case-mini">사무실 · 상가청소</div>

          <div class="case-mini">특수청소 작업사례</div>
          <div class="case-mini">쓰레기집 정리 전후사진</div>
          <div class="case-mini">비둘기 퇴치 전후사진</div>
          <div class="case-mini">유품정리 작업사례</div>
          <div class="case-mini">고독사 특수청소</div>
          <div class="case-mini">폐기물 처리 사례</div>
          <div class="case-mini">입주청소 전후사진</div>
          <div class="case-mini">사무실 · 상가청소</div>
        </div>
      </div>'''
s = s.replace(portfolio_old, portfolio_new)

price_old = '''<div class="price-grid">
        <div class="price-card">
          <h3>입주 · 이사청소</h3>
          <div class="price-row"><span>원룸 · 1.5룸 · 투룸</span><span>사진 확인 후 안내</span></div>
          <div class="price-row"><span>아파트 · 빌라 · 주택</span><span>평수 확인 후 안내</span></div>
          <div class="price-row"><span>심한 오염 · 짐 있는 현장</span><span>상담 후 안내</span></div>
        </div>

        <div class="price-card">
          <h3>쓰레기집 청소</h3>
          <div class="price-row"><span>생활쓰레기 · 폐기물 양</span><span>사진 확인 후 안내</span></div>
          <div class="price-row"><span>악취 · 바닥 오염 · 분리배출</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>쓰리룸 이상 또는 대량 폐기물</span><span>방문견적</span></div>
        </div>

        <div class="price-card">
          <h3>비둘기 퇴치</h3>
          <div class="price-row"><span>분변 제거</span><span>현장 확인 후 안내</span></div>
          <div class="price-row"><span>둥지·알·새끼 확인</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>유입경로 차단막 · 스카이 장비</span><span>별도 안내</span></div>
        </div>

        <div class="price-card">
          <h3>특수청소 · 유품정리</h3>
          <div class="price-row"><span>오염 범위 · 악취 · 폐기물</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>고독사 특수청소</span><span>현장 확인 후 안내</span></div>
          <div class="price-row"><span>유품정리 · 폐기물 처리</span><span>작업 범위 확인 후 안내</span></div>
        </div>
      </div>'''
price_new = '''<div class="price-grid">
        <div class="price-card">
          <h3>특수청소 · 유품정리</h3>
          <div class="price-row"><span>오염 범위 · 악취 · 폐기물</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>고독사 특수청소</span><span>현장 확인 후 안내</span></div>
          <div class="price-row"><span>유품정리 · 폐기물 처리</span><span>작업 범위 확인 후 안내</span></div>
        </div>

        <div class="price-card">
          <h3>쓰레기집 청소</h3>
          <div class="price-row"><span>생활쓰레기 · 폐기물 양</span><span>사진 확인 후 안내</span></div>
          <div class="price-row"><span>악취 · 바닥 오염 · 분리배출</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>쓰리룸 이상 또는 대량 폐기물</span><span>방문견적</span></div>
        </div>

        <div class="price-card">
          <h3>비둘기 퇴치</h3>
          <div class="price-row"><span>분변 제거</span><span>현장 확인 후 안내</span></div>
          <div class="price-row"><span>둥지·알·새끼 확인</span><span>상담 후 안내</span></div>
          <div class="price-row"><span>유입경로 차단막 · 스카이 장비</span><span>별도 안내</span></div>
        </div>

        <div class="price-card">
          <h3>입주 · 이사청소</h3>
          <div class="price-row"><span>원룸 · 1.5룸 · 투룸</span><span>사진 확인 후 안내</span></div>
          <div class="price-row"><span>아파트 · 빌라 · 주택</span><span>평수 확인 후 안내</span></div>
          <div class="price-row"><span>심한 오염 · 짐 있는 현장</span><span>상담 후 안내</span></div>
        </div>
      </div>'''
s = s.replace(price_old, price_new)

faq_insert_after = '<div class="faq-grid">\n'
if '<b>특수청소란 무엇인가요?</b>' not in s:
    special_faq = '''        <div class="faq-card"><b>특수청소란 무엇인가요?</b><p>특수청소는 생활 오염을 닦는 일반 청소와 달리 악취, 폐기물, 배설물, 그을음, 장기간 방치된 오염처럼 현장 상태를 먼저 판단해야 하는 청소입니다. 작업 전 사진과 영상을 확인해 범위와 위험 요소를 먼저 안내합니다.</p></div>
        <div class="faq-card"><b>쓰레기집 청소는 어떻게 진행되나요?</b><p>폐기물 양, 바닥 오염, 악취, 출입 조건을 먼저 확인합니다. 현장 상태에 따라 분리배출, 폐기물 처리, 바닥 청소, 추가 소독·탈취 가능 여부를 안내합니다.</p></div>
        <div class="faq-card"><b>비둘기 배설물 청소는 왜 따로 확인하나요?</b><p>비둘기 배설물은 냄새와 오염뿐 아니라 둥지, 알·새끼, 재유입 경로를 함께 봐야 합니다. 분변 제거만 필요한지, 차단 작업이 필요한지 사진으로 먼저 확인합니다.</p></div>
'''
    s = s.replace(faq_insert_after, faq_insert_after + special_faq, 1)

extra = '''<article class="journal-card"><span>비둘기 퇴치</span><h3>비둘기 퇴치 전 확인할 사항</h3><p>분변 위치, 둥지 여부, 외부 난간 작업 가능 여부, 작업 가능 범위를 상담 전에 확인합니다.</p><p>분변·둥지·작업 가능 범위 기준으로 정리합니다.</p></article><article class="journal-card"><span>특수청소</span><h3>특수청소 상담 전 알려주면 좋은 내용</h3><p>오염 범위, 냄새 정도, 폐기물 양, 출입 가능 시간, 엘리베이터 사용 여부를 먼저 확인하면 상담이 빨라집니다.</p><p>오염 범위와 출입 조건을 기준으로 정리합니다.</p></article>'''
if '비둘기 퇴치 전 확인할 사항' not in s:
    s = s.replace('</div></div></section>\n<section id="policy"', extra + '</div></div></section>\n<section id="policy"', 1)

review_css = '''
/* REVIEW_TEXT_SWIPE */
.review-text-section{margin:34px auto 0;max-width:1100px;text-align:left}
.review-text-section h3{font-size:24px;margin:0 0 8px;color:#0f172a}
.review-text-lead{margin:0 0 16px;color:#64748b;line-height:1.7;font-size:15px}
.review-text-scroll{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 6px 18px;margin:0 -6px;scrollbar-width:none;cursor:grab;-webkit-overflow-scrolling:touch}
.review-text-scroll::-webkit-scrollbar{display:none}
.review-text-scroll:active{cursor:grabbing}
.review-text-card{flex:0 0 320px;scroll-snap-align:start;background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);text-align:left}
.review-text-card b{display:block;margin:0 0 12px;color:#0f172a;font-size:17px;line-height:1.45}
.review-text-card p{margin:0;color:#334155;line-height:1.72;font-size:16px;font-weight:800}
.review-text-hint{margin:0;color:#94a3b8;font-size:13px;font-weight:800}
@media(max-width:760px){.review-text-section{margin-top:28px}.review-text-card{flex-basis:82vw;max-width:340px;padding:20px}.review-text-card b{font-size:16px}.review-text-card p{font-size:15.5px}.review-text-hint{font-size:12px}}
'''.strip()

special_css = '''
/* SPECIAL_CLEANING_POSITIONING */
.hero-main{margin:0 auto 24px;letter-spacing:-.04em}
.service-special-note{font-weight:900;color:#0f172a}
'''.strip()

review_html = '''
<!-- REVIEW_TEXT_SWIPE_BLOCK_START -->
<section class="review-text-section" aria-label="텍스트 고객 후기">
  <h3>짧은 고객 후기</h3>
  <p class="review-text-lead">사진 후기 아래에 실제 후기 문구를 함께 정리했습니다.</p>
  <div class="review-text-scroll" aria-label="고객 후기 텍스트 슬라이드">
    <article class="review-text-card">
      <b>인천 입주청소 고객 후기</b>
      <p>“친절하게 설명해주시고 깨끗하게 해주셔서 감사합니다.”</p>
    </article>
    <article class="review-text-card">
      <b>부평 이사청소 고객 후기</b>
      <p>“사진으로 먼저 상담받을 수 있어서 편했어요.”</p>
    </article>
    <article class="review-text-card">
      <b>인천 비둘기 퇴치 고객 후기</b>
      <p>“설명 듣고 진행해서 걱정이 덜했어요.”</p>
    </article>
    <article class="review-text-card">
      <b>쓰레기집 청소 고객 후기</b>
      <p>“어디서부터 해야 할지 막막했는데 정리해주셔서 감사합니다.”</p>
    </article>
  </div>
  <p class="review-text-hint">옆으로 넘겨서 후기를 확인하실 수 있습니다.</p>
</section>
<!-- REVIEW_TEXT_SWIPE_BLOCK_END -->
'''.strip()

review_js_body = '''
/* REVIEW_TEXT_DRAG */
(function(){
  function initReviewTextDrag(){
    document.querySelectorAll('.review-text-scroll').forEach(function(el){
      if(el.dataset.dragReady){return;}
      el.dataset.dragReady='1';
      var down=false,startX=0,startScroll=0;
      el.addEventListener('pointerdown',function(e){
        down=true;startX=e.clientX;startScroll=el.scrollLeft;el.classList.add('is-dragging');
        try{el.setPointerCapture(e.pointerId);}catch(err){}
      });
      el.addEventListener('pointermove',function(e){
        if(!down){return;}
        el.scrollLeft=startScroll-(e.clientX-startX);
      });
      function stop(){down=false;el.classList.remove('is-dragging');}
      el.addEventListener('pointerup',stop);
      el.addEventListener('pointercancel',stop);
      el.addEventListener('mouseleave',function(){if(down){stop();}});
    });
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',initReviewTextDrag);}else{initReviewTextDrag();}
})();
'''.strip()

# Remove the earlier misplaced drag script if it was inserted into the JSON-LD script.
old_review_js = '''

    /* REVIEW_TEXT_DRAG */
    (function(){
      function initReviewTextDrag(){
        document.querySelectorAll('.review-text-scroll').forEach(function(el){
          if(el.dataset.dragReady){return;}
          el.dataset.dragReady='1';
          var down=false,startX=0,startScroll=0;
          el.addEventListener('pointerdown',function(e){
            down=true;startX=e.clientX;startScroll=el.scrollLeft;el.classList.add('is-dragging');
            try{el.setPointerCapture(e.pointerId);}catch(err){}
          });
          el.addEventListener('pointermove',function(e){
            if(!down){return;}
            el.scrollLeft=startScroll-(e.clientX-startX);
          });
          function stop(){down=false;el.classList.remove('is-dragging');}
          el.addEventListener('pointerup',stop);
          el.addEventListener('pointercancel',stop);
          el.addEventListener('mouseleave',function(){if(down){stop();}});
        });
      }
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',initReviewTextDrag);}else{initReviewTextDrag();}
    })();
'''.rstrip()
s = s.replace(old_review_js, '')

if '/* REVIEW_TEXT_SWIPE */' not in s:
    s = s.replace('</style>', review_css + '\n</style>', 1)

if '/* SPECIAL_CLEANING_POSITIONING */' not in s:
    s = s.replace('</style>', special_css + '\n</style>', 1)

start = '<!-- REVIEW_TEXT_SWIPE_BLOCK_START -->'
end = '<!-- REVIEW_TEXT_SWIPE_BLOCK_END -->'
if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + review_html + s[b:]
else:
    marker = '\n    </div>\n  </section>\n<section id="journal"'
    review_pos = s.index('<div class="review-marquee"')
    insert_pos = s.index(marker, review_pos)
    s = s[:insert_pos] + '\n' + review_html + s[insert_pos:]

if '/* REVIEW_TEXT_DRAG */' not in s:
    s = s.replace('</body>', '<script>\n' + review_js_body + '\n</script>\n</body>', 1)

p.write_text(s, encoding='utf-8')
