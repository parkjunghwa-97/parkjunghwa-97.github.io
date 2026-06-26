from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove accidentally inserted page-navigation JavaScript from the first JSON-LD block.
s = s.replace('''\n    window.addEventListener('popstate', function(){\n      const id=(location.hash||'#home').replace('#','');\n      if(document.getElementById(id)){showPage(id,true);}\n    });\n    document.addEventListener('DOMContentLoaded', function(){\n      const id=(location.hash||'').replace('#','');\n      if(id && document.getElementById(id)){showPage(id,true);}\n    });\n''', '\n')

# Home/top-left brand badge
old_brand = '<div class="nav-brand" onclick="showPage(\'home\')">대한청소만세</div>'
new_brand = '''<div class="nav-brand" onclick="showPage('home')">
      <span class="nav-brand-main">대한청소만세</span>
      <span class="nav-brand-cert">중소벤처기업부 여성기업 확인</span>
    </div>'''
if 'nav-brand-cert' not in s:
    s = s.replace(old_brand, new_brand, 1)

brand_css = r'''

    /* BRAND_CERT_BADGE */
    .nav-brand{display:flex;flex-direction:column;line-height:1.12;align-items:flex-start}
    .nav-brand-main{font-weight:950;font-size:18px;white-space:nowrap}
    .nav-brand-cert{margin-top:4px;font-size:11px;font-weight:850;color:#cbd5e1;letter-spacing:-.02em;white-space:nowrap}
    @media(max-width:760px){.nav-brand{display:flex!important;align-items:center;justify-content:center;margin-bottom:12px}.nav-brand-main{font-size:22px}.nav-brand-cert{font-size:11px;margin-top:4px}}
'''
if '/* BRAND_CERT_BADGE */' not in s:
    s = s.replace('</style>', brand_css + '\n</style>', 1)

css = r'''

    /* CERT_TRUST_SECTION */
    .cert-trust{margin:34px auto 0;padding:26px 0 0;border-top:1px solid #cbd5e1;text-align:center;color:#0f172a;max-width:860px}
    .cert-trust-title{font-size:17px;font-weight:950;letter-spacing:-.02em;margin-bottom:8px}
    .cert-trust-people{font-size:15px;color:#475569;font-weight:850;margin-bottom:18px}
    .cert-trust-people span{display:inline-block;margin:0 10px;color:#94a3b8}
    .cert-actions{display:none!important}
    @media(max-width:760px){.cert-trust{margin:24px auto 0;padding-top:18px}.cert-trust-title{font-size:15px}.cert-trust-people{font-size:13.5px;margin-bottom:0}.cert-trust-people span{margin:0 6px}}
'''

if '/* CERT_TRUST_SECTION */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

cleanup_css = r'''

    /* CERT_TRUST_CLEANUP */
    .cert-trust{margin:28px auto 0!important;padding:18px 0 0!important;border-top:1px solid #d7dee8!important;background:transparent!important;box-shadow:none!important;max-width:760px!important}
    .cert-trust-title{font-size:15.5px!important;font-weight:900!important;color:#0f172a!important;letter-spacing:-.03em!important;margin-bottom:6px!important}
    .cert-trust-people{font-size:13.5px!important;color:#64748b!important;font-weight:800!important;margin-bottom:0!important}
    .cert-actions{display:none!important}
    .cert-toggle,.cert-view,.cert-person,.cert-thumbs{display:none!important}
    @media(max-width:760px){.cert-trust{margin-top:22px!important;padding-top:16px!important}.cert-trust-title{font-size:14.5px!important}.cert-trust-people{font-size:12.8px!important}}
'''
if '/* CERT_TRUST_CLEANUP */' not in s:
    s = s.replace('</style>', cleanup_css + '\n</style>', 1)

partner_css = r'''

    /* PARTNER_SYSTEM_BAR */
    .partner-system{margin:18px auto 24px;padding:18px 0;border-top:1px solid #cbd5e1;border-bottom:1px solid #e2e8f0;text-align:center;max-width:850px;color:#0f172a}
    .partner-system b{display:block;font-size:17px;line-height:1.55;margin-bottom:8px;color:#0f172a}
    .partner-system p{margin:0;color:#475569;line-height:1.75;font-size:15px;font-weight:750}
    @media(max-width:760px){.partner-system{margin:16px auto 22px;padding:16px 0}.partner-system b{font-size:15.5px}.partner-system p{font-size:14.5px}}
'''
if '/* PARTNER_SYSTEM_BAR */' not in s:
    s = s.replace('</style>', partner_css + '\n</style>', 1)

html = r'''

          <div class="cert-trust" aria-label="여성기업 확인 및 관련 자격 안내">
            <div class="cert-trust-title">여성기업 확인 업체 · 관련 자격 보유</div>
            <div class="cert-trust-people">대표 박정화 <span>|</span> 총괄대표 김수현</div>
            <div class="cert-actions">
              <details class="cert-toggle">
                <summary>여성기업 확인서 보기</summary>
                <div class="cert-view cert-view-single">
                  <img decoding="async" loading="lazy" src="images/certificates/certificates/women-company.jpg" alt="기프트클린 대한청소만세 여성기업 확인서">
                </div>
              </details>
              <details class="cert-toggle">
                <summary>관련 자격 보기</summary>
                <div class="cert-view">
                  <div class="cert-person">
                    <b>대표 박정화</b>
                    <div class="cert-thumbs">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/park-clean.jpg" alt="박정화 청소전문가 1급 자격증">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/park-pest.jpg" alt="박정화 방역관리사 1급 자격증">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/park-estate.jpg" alt="박정화 유품정리사 1급 자격증">
                    </div>
                  </div>
                  <div class="cert-person">
                    <b>총괄대표 김수현</b>
                    <div class="cert-thumbs">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-clean.jpg" alt="김수현 청소전문가 1급 자격증">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-pest.jpg" alt="김수현 방역관리사 1급 자격증">
                      <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-estate.jpg" alt="김수현 유품정리사 1급 자격증">
                    </div>
                  </div>
                </div>
              </details>
            </div>
          </div>
'''

anchor = '<div class="about-ending">깨끗한 공간,<br>새로운 시작을 선물합니다.</div>'
if 'aria-label="여성기업 확인 및 관련 자격 안내"' not in s and anchor in s:
    s = s.replace(anchor, anchor + html, 1)

old_partner_sub = '<p class="sub">대한청소만세의 현장 기준을 함께 배워갈 지역 파트너를 기다립니다.</p>'
new_partner_sub = '<p class="sub">체계적으로 함께할 지역 파트너를 찾습니다.</p>'
s = s.replace(old_partner_sub, new_partner_sub, 1)

partner_block = '''

      <div class="partner-system">
        <b>여성기업 확인 업체 · 자체 현장관리 프로그램 운영</b>
        <p>자체 현장관리 프로그램으로 일정, 현장 정보, 작업 내용, 정산 흐름을 기록하고 공유합니다.<br>함께하는 파트너가 현장에 집중할 수 있도록 상담부터 일정 공유, 작업 안내, 정산까지 명확하게 운영합니다.</p>
      </div>
'''
partner_anchor = '''      <div class="trust-box partner-hero">
        <b>청소 기술만으로는 부족합니다.<br>현장을 운영하는 기준이 필요합니다.</b>
        <p>현장을 대하는 태도, 고객에게 안내하는 방식,<br>추가 작업을 설명하는 기준까지 함께 배워갑니다.</p>
      </div>'''
if '자체 현장관리 프로그램으로 일정' not in s and partner_anchor in s:
    s = s.replace(partner_anchor, partner_anchor + partner_block, 1)

p.write_text(s, encoding='utf-8')
