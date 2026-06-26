from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 문구 정리
s = re.sub(r'(· 쓰레기집 청소)(?: · 쓰레기집 청소)+', r'\1', s)
s = s.replace('폐기물 처리 비용 안내', '폐기물 처리')
s = s.replace('작업 범위는 상담 기준으로 진행돼요를 확인해 예상 견적을 안내드립니다.', '작업 범위를 확인해 예상 견적을 안내드립니다.')
s = s.replace('<b>사업장 기준</b>', '<b>사업장</b>')

# 이미지 lazy loading. 인트로 로고 제외.
def lazy_img(m):
    tag = m.group(0)
    if 'intro-logo' in tag:
        return tag
    if 'loading=' not in tag:
        tag = tag.replace('<img', '<img loading="lazy"', 1)
    if 'decoding=' not in tag:
        tag = tag.replace('<img', '<img decoding="async"', 1)
    return tag
s = re.sub(r'<img\b[^>]*>', lazy_img, s)

# 네비게이션에 현장일지 추가
s = re.sub(r'\n\s*<button class="nav-btn" onclick="showPage\(\'journal\'\)">현장일지</button>', '', s)
s = s.replace('<button class="nav-btn" onclick="showPage(\'portfolio\')">작업사례</button>\n      <button class="nav-btn" onclick="showPage(\'policy\')">FAQ</button>', '<button class="nav-btn" onclick="showPage(\'portfolio\')">작업사례</button>\n      <button class="nav-btn" onclick="showPage(\'journal\')">현장일지</button>\n      <button class="nav-btn" onclick="showPage(\'policy\')">FAQ</button>', 1)

# 현장일지 섹션
journal = '''  <section id="journal" class="page journal-page"><div class="page-inner"><h2>현장일지</h2><p class="sub">실제 현장 기록을 지역, 서비스, 작업 범위 중심의 텍스트로 쌓아가는 공간입니다.</p><div class="journal-grid"><article class="journal-card"><span>작성 예시</span><h3>인천 부평 입주청소 현장일지</h3><p>평수, 오염 상태, 작업 범위, 추가 안내사항을 정리해 실제 작업사례 글로 확장합니다.</p><a href="/cases/">현장일지 구조 보기</a></article><article class="journal-card"><span>작성 예시</span><h3>송도 정리 청소 현장일지</h3><p>폐기물 양, 냄새, 바닥 오염, 작업 인원과 시간을 텍스트로 기록하는 구조입니다.</p><a href="/cases/">작업사례 템플릿 보기</a></article><article class="journal-card"><span>작성 예시</span><h3>비둘기 퇴치 작업일지</h3><p>분변 제거, 둥지 확인, 유입경로 차단막 설치 여부를 현장별로 남길 수 있습니다.</p><a href="/cases/">상세 구조 보기</a></article></div></div></section>'''
s = re.sub(r'\n\s*<section id="journal" class="page journal-page">.*?</section>\s*', '\n', s, flags=re.S)
s = s.replace('  <section id="policy" class="page">', journal + '\n\n  <section id="policy" class="page">', 1)

# 후기 텍스트 요약 영역
review_text = '''
      <div class="review-text-section" aria-label="텍스트 고객 후기 요약"><h3>후기 텍스트 요약</h3><p class="review-text-lead">후기 이미지는 유지하고, 검색엔진과 AI가 읽을 수 있도록 후기 내용을 텍스트로도 정리합니다.</p><div class="review-text-grid"><article class="review-text-card"><b>입주청소 후기</b><p>서울·경기·인천 입주청소 상담 후 현장 상태와 작업 범위를 확인하고 진행한 후기입니다. 실제 후기 문구는 확인 후 순차적으로 추가합니다.</p><span>입주청소 · 이사청소 · 수도권</span></article><article class="review-text-card"><b>비둘기 퇴치 후기</b><p>분변 제거, 둥지 확인, 유입경로 차단막 설치 등 현장 상태에 맞춰 안내한 후기입니다.</p><span>비둘기 퇴치 · 분변 제거 · 차단망</span></article><article class="review-text-card"><b>정리 청소 후기</b><p>생활 오염, 냄새, 폐기물 양, 바닥 오염을 확인한 뒤 작업 범위와 예상 견적을 안내한 후기입니다.</p><span>정리 청소 · 폐기물 처리 · 냄새</span></article></div></div>'''
s = re.sub(r'\n\s*<div class="review-text-section".*?</div>\s*(?=\n\s*</div>\s*</section>\s*\n\s*<section id="policy")', '\n', s, flags=re.S)
s = re.sub(r'(</div>\s*</div>\s*</div>\s*</section>\s*\n\s*<section id="journal")', review_text + r'\n    \1', s, count=1, flags=re.S)

# 푸터 지역 텍스트
footer_local = '''    <div class="footer-local" aria-label="주요 서비스 지역"><b>주요 서비스 지역</b><p>서울 · 경기 · 인천 / 부평 · 부천 · 송도 · 청라 · 검단 · 계양 · 수원 · 용인 · 성남 · 고양 · 김포 · 파주 · 안산 · 시흥 · 화성 · 평택</p><p>전국 출장 상담 가능 서비스: 특수청소 · 유품정리 · 정리 청소 · 폐기물 처리 · 비둘기 퇴치</p></div>'''
s = re.sub(r'\n\s*<div class="footer-local".*?</div>\s*', '\n', s, flags=re.S)
s = s.replace('    <div class="company-info">', footer_local + '\n    <div class="company-info">', 1)

# 추가 CSS
css = '''
    /* GROWTH_SEO_SECTIONS */
    .journal-grid,.review-text-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}.journal-card,.review-text-card{background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);text-align:left}.journal-card h3,.review-text-card b{margin:0 0 10px;color:#0f172a;font-size:18px}.journal-card p,.review-text-card p{margin:0;color:#64748b;line-height:1.75;font-size:15px}.journal-card span,.review-text-card span{display:inline-block;margin:12px 0 0;color:#334155;background:#f1f5f9;border-radius:999px;padding:7px 10px;font-size:13px;font-weight:900}.journal-card a{display:inline-flex;margin-top:16px;font-weight:950;color:#0f172a}.review-text-section{margin:30px auto 0;max-width:980px;text-align:left}.review-text-section h3{font-size:24px;margin:0 0 8px;color:#0f172a}.review-text-lead{margin:0 0 16px;color:#64748b;line-height:1.7}.footer-local{max-width:900px;margin:0 auto 18px;padding:18px;border-radius:22px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);color:#e5e7eb;line-height:1.7}.footer-local b{display:block;color:#fff;margin-bottom:8px}.footer-local p{margin:6px 0;color:#cbd5e1;font-size:14px}@media(max-width:760px){.journal-grid,.review-text-grid{grid-template-columns:1fr}}
'''
s = re.sub(r'\n\s*/\* GROWTH_SEO_SECTIONS \*/.*?(?=\n\s*/\* MOBILE_NAV_FLOW_FIX \*/|\n\s*/\* PARTNER_SECTION \*/|\n\s*</style>)', '\n', s, flags=re.S)
s = s.replace('    /* MOBILE_NAV_FLOW_FIX */', css + '\n    /* MOBILE_NAV_FLOW_FIX */', 1) if '    /* MOBILE_NAV_FLOW_FIX */' in s else s.replace('</style>', css + '\n  </style>', 1)

p.write_text(s, encoding='utf-8')
