from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep the cost guide menu, but do not publish prices until they are finalized.
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
    .price-row span:last-child{font-weight:900;color:#0f172a;white-space:nowrap;text-align:right}
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
      <p class="sub price-lead">청소 비용은 평수, 오염도, 짐 유무, 폐기물 양, 작업 범위, 장비 사용 여부에 따라 달라집니다. 확정되지 않은 금액을 먼저 안내하기보다 사진과 현장 상태를 확인한 뒤 예상 비용을 안내드립니다.</p>

      <div class="price-grid">
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
      </div>

      <div class="price-note">
        <p>※ 아직 확정된 가격표가 아닌 상담 기준 안내입니다.</p>
        <p>※ 현장 상황 및 오염도에 따라 비용이 달라질 수 있습니다.</p>
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

if 'id="price"' in s:
    s = re.sub(
        r'\n\s*<section id="price" class="page price-page">.*?</section>\s*(?=\n\s*<section id="portfolio" class="page">)',
        price_section,
        s,
        count=1,
        flags=re.S
    )
else:
    s = s.replace('\n  <section id="portfolio" class="page">', price_section + '\n  <section id="portfolio" class="page">', 1)

p.write_text(s, encoding='utf-8')
