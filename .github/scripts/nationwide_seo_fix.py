from pathlib import Path
import re
p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '<button class="nav-btn" onclick="showPage(\'contact\')">상담문의</button>'
new = '<button class="nav-btn" onclick="showPage(\'partner\')">파트너모집</button>\n      ' + old
s = s.replace('<button class="nav-btn" onclick="location.href=\'partner.html\'">파트너모집</button>', '<button class="nav-btn" onclick="showPage(\'partner\')">파트너모집</button>')
if "showPage('partner')" not in s:
    s = s.replace(old, new, 1)

hero_html = '''<div class="hero-main">낮은 견적보다 중요한 건,<br>불안하지 않은 과정입니다.</div>

      <div class="hero-sub">사진 상담으로 현장 상태를 먼저 확인하고<br>작업 범위와 추가 비용 가능성을 안내합니다.<br><br>서울·경기·인천 입주청소 · 이사청소<br>전국 특수청소 · 유품정리 · 고독사청소</div>

      <div class="hero-cta">
        <button class="hero-btn" onclick="showPage('contact')">내 상황 상담받기</button>
        <button class="hero-btn secondary" onclick="showPage('portfolio')">작업사례 보기</button>
      </div>

      <div class="hero-proof">동의 없는 추가 작업은 진행하지 않습니다.</div>'''
s = re.sub(r'(<section id="home" class="page hero">\s*<div class="hero-inner">\s*).*?(\s*<div class="social-icons">)', r'\1' + hero_html + r'\2', s, count=1, flags=re.S)

s = s.replace('<p class="sub">상담 전 많이 물어보시는 내용을 먼저 정리했습니다.</p>', '')
s = re.sub(r'\n\s*<p class="more-info-intro">.*?</p>', '', s, count=1, flags=re.S)

repls = {
    '<summary>예약은 이렇게 진행돼요</summary>': '<summary>예약 안내</summary>',
    '<summary>예약금 환불은 이렇게 안내드려요</summary>': '<summary>예약금 환불 기준</summary>',
    '<summary>작업 당일 취소·환불 안내</summary>': '<summary>현장 환불 기준</summary>',
    '<summary>사진 견적은 예상 견적이에요</summary>': '<summary>사진 견적 안내</summary>',
    '<summary>현장 상태를 미리 알려주세요</summary>': '<summary>현장 상태 고지 의무</summary>',
    '<summary>작업 범위는 상담 기준으로 진행돼요</summary>': '<summary>작업 범위</summary>',
    '<summary>추가비용이 생길 수 있는 경우</summary>': '<summary>추가 비용 발생 가능 항목</summary>',
    '<summary>작업 전 준비해주시면 좋아요</summary>': '<summary>고객 준비사항</summary>',
    '<summary>작업 후 확인 안내</summary>': '<summary>작업 결과 확인</summary>',
    '<summary>비대면 작업 안내</summary>': '<summary>비대면 작업</summary>',
    '<summary>A/S 접수 안내</summary>': '<summary>A/S 정책</summary>',
    '<summary>A/S가 어려운 경우</summary>': '<summary>A/S 제외 항목</summary>',
    '<summary>폐기물 처리 비용 안내</summary>': '<summary>폐기물 처리</summary>',
    '<summary>유품·귀중품은 먼저 확인해주세요</summary>': '<summary>유품 및 귀중품 관련 안내</summary>'
}
for a,b in repls.items():
    s = s.replace(a,b)

fixes = {
    '작업 범위는 상담 기준으로 진행돼요 내': '작업 범위 내',
    '작업 범위는 상담 기준으로 진행돼요에 대한': '작업 범위에 대한',
    '작업 범위는 상담 기준으로 진행돼요와': '작업 범위와',
    '예약금 환불은 이렇게 안내드려요 적용': '예약금 환불 기준 적용',
    '비대면 작업 안내 시': '비대면 작업 시',
    '비대면 작업 안내 완료 후에는': '비대면 작업 완료 후에는',
    '폐기물 처리 비용 안내 비용': '폐기물 처리 비용',
    '폐기물 처리 비용 안내</b>': '폐기물 처리</b>',
    '오염도와 작업 범위는 상담 기준으로 진행돼요 확인': '오염도와 작업 범위 확인'
}
for a,b in fixes.items():
    s = s.replace(a,b)

partner = '''
  <section id="partner" class="page partner-page">
    <div class="page-inner">
      <h2>파트너 모집</h2>
      <p class="sub">대한청소만세의 현장 기준을 함께 배워갈 지역 파트너를 기다립니다.</p>

      <div class="trust-box partner-hero">
        <b>청소 기술만으로는 부족합니다.<br>현장을 운영하는 기준이 필요합니다.</b>
        <p>현장을 대하는 태도, 고객에게 안내하는 방식,<br>추가 작업을 설명하는 기준까지 함께 배워갑니다.</p>
      </div>

      <div class="partner-grid">
        <div class="partner-card">
          <b>누가 지원하면 좋나요?</b>
          <ul>
            <li>청소 일을 제대로 배워 오래 해보고 싶은 분</li>
            <li>고객 응대와 약속 시간을 중요하게 생각하는 분</li>
            <li>혼자 일하더라도 현장 기준이 필요한 분</li>
            <li>지역에서 꾸준히 청소 일을 키워가고 싶은 분</li>
          </ul>
        </div>

        <div class="partner-card">
          <b>무엇을 배우나요?</b>
          <ul>
            <li>사진 상담으로 현장 상태를 보는 법</li>
            <li>작업 범위와 추가 비용을 안내하는 기준</li>
            <li>입주·이사청소 기본 작업 흐름</li>
            <li>쓰레기집·특수현장 상담 시 주의할 점</li>
            <li>작업 후 확인, 후기, 고객 응대 방식</li>
          </ul>
        </div>

        <div class="partner-card">
          <b>지역 파트너가 되면</b>
          <ul>
            <li>가능 지역과 가능한 작업을 먼저 확인합니다.</li>
            <li>대한청소만세의 상담·작업 기준을 공유합니다.</li>
            <li>현장 경험과 준비 상태에 따라 협업 범위를 정합니다.</li>
            <li>무리한 현장보다 가능한 현장부터 시작합니다.</li>
          </ul>
        </div>

        <div class="partner-card">
          <b>문의 후 절차</b>
          <ol>
            <li>카카오톡으로 파트너 문의</li>
            <li>지역·경험·가능 작업 확인</li>
            <li>전화 또는 카톡 상담</li>
            <li>현장 기준 안내</li>
            <li>협업 가능 여부 확인</li>
          </ol>
        </div>
      </div>

      <div class="partner-note">처음부터 모든 현장을 맡기는 방식이 아니라,<br>가능한 작업과 지역을 확인한 뒤 단계적으로 협의합니다.</div>
      <a class="apply-btn" href="https://pf.kakao.com/_lxhwGX" target="_blank">파트너 문의하기</a>
    </div>
  </section>

'''
s = re.sub(r'\n\s*<section id="partner" class="page[^\"]*">.*?</section>\s*', '\n', s, flags=re.S)
m = re.search(r'\n\s*<section id="contact" class="page">', s)
if m:
    s = s[:m.start()] + '\n' + partner + s[m.start():]
else:
    s = s.replace('<section id="contact" class="page">', partner + '<section id="contact" class="page">', 1)

bar = '''<div class="fixed-contact-bar">
    <a href="tel:010-4122-9207">전화 상담</a>
    <a class="kakao" href="https://pf.kakao.com/_lxhwGX" target="_blank">카톡 상담</a>
  </div>'''
s = re.sub(r'\s*<a class="fixed-call" href="tel:010-4122-9207">📞 상담</a>\s*', '\n  ' + bar + '\n', s, count=1)
s = re.sub(r'<div class="fixed-contact-bar">.*?</div>', bar, s, count=1, flags=re.S)

css = '''
    /* MOBILE_NAV_FLOW_FIX */
    @media(max-width:760px){
      .top-nav{position:sticky;top:0;left:auto;right:auto}
      .page,.hero{padding-top:36px}
      #portfolio{padding-top:36px}
    }
    /* PARTNER_SECTION */
    .partner-page .page-inner{max-width:960px}
    .partner-hero{margin-top:24px;margin-bottom:20px}
    .partner-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:20px 0 22px;text-align:left}
    .partner-card{background:#fff;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);border:1px solid rgba(226,232,240,.9)}
    .partner-card b{display:block;font-size:18px;color:#0f172a;margin-bottom:12px}
    .partner-card ul,.partner-card ol{margin:0;padding-left:18px;color:#475569;line-height:1.75;font-size:15px}
    .partner-note{margin:18px 0 22px;padding:18px;border-radius:20px;background:#f8fafc;border:1px solid #e2e8f0;color:#475569;line-height:1.7;font-weight:800}
    /* FIXED_CONTACT_BAR */
    .fixed-contact-bar{position:fixed;right:16px;bottom:82px;z-index:999;display:flex;flex-direction:column;gap:8px;background:rgba(15,23,42,.94);padding:9px;border-radius:22px;box-shadow:0 12px 30px rgba(0,0,0,.25);backdrop-filter:blur(8px);width:150px}
    .fixed-contact-bar a{text-align:center;border-radius:999px;padding:12px 10px;background:#fff;color:#0f172a;font-weight:950;font-size:14px;text-decoration:none}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:76px;width:142px}.fixed-contact-bar a{font-size:14px;padding:12px 8px}footer{padding-bottom:170px}.fixed-call{display:none}}
'''
s = re.sub(r'\n\s*/\* MOBILE_NAV_FLOW_FIX \*/.*?/\* FIXED_CONTACT_BAR \*/.*?(?=\n\s*</style>)', '\n' + css, s, count=1, flags=re.S)
s = re.sub(r'\n\s*/\* MOBILE_NAV_FLOW_FIX \*/.*?/\* PARTNER_SECTION \*/.*?/\* FIXED_CONTACT_BAR \*/.*?(?=\n\s*</style>)', '\n' + css, s, count=1, flags=re.S)
if 'MOBILE_NAV_FLOW_FIX' not in s:
    s = s.replace('\n  </style>', css + '\n  </style>', 1)
elif 'PARTNER_SECTION' not in s:
    s = s.replace('\n  </style>', '\n' + css + '\n  </style>', 1)

p.write_text(s, encoding='utf-8')
