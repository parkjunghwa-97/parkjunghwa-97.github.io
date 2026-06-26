from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove accidentally inserted page-navigation JavaScript from the first JSON-LD block.
s = s.replace('''\n    window.addEventListener('popstate', function(){\n      const id=(location.hash||'#home').replace('#','');\n      if(document.getElementById(id)){showPage(id,true);}\n    });\n    document.addEventListener('DOMContentLoaded', function(){\n      const id=(location.hash||'').replace('#','');\n      if(id && document.getElementById(id)){showPage(id,true);}\n    });\n''', '\n')

css = r'''

    /* CERT_TRUST_SECTION */
    .cert-trust{margin:34px auto 0;padding:26px 0 0;border-top:1px solid #cbd5e1;text-align:center;color:#0f172a;max-width:860px}
    .cert-trust-title{font-size:17px;font-weight:950;letter-spacing:-.02em;margin-bottom:8px}
    .cert-trust-people{font-size:15px;color:#475569;font-weight:850;margin-bottom:18px}
    .cert-trust-people span{display:inline-block;margin:0 10px;color:#94a3b8}
    .cert-actions{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;align-items:flex-start}
    .cert-toggle{display:inline-block;text-align:center}
    .cert-toggle summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;min-width:154px;padding:11px 16px;border-radius:999px;background:#0f172a;color:#fff;font-weight:950;font-size:14px;box-shadow:0 8px 18px rgba(15,23,42,.16)}
    .cert-toggle summary::-webkit-details-marker{display:none}
    .cert-toggle[open] summary{background:#334155}
    .cert-view{width:min(860px,calc(100vw - 72px));margin:16px auto 0;padding:18px 0 0;border-top:1px solid #e2e8f0;text-align:center}
    .cert-view-single img{width:min(280px,80vw);height:auto;border:1px solid #e2e8f0;background:#fff;box-shadow:0 6px 18px rgba(15,23,42,.08)}
    .cert-person{margin:0 0 20px;text-align:left}
    .cert-person b{display:block;margin:0 0 10px;color:#0f172a;font-size:15px}
    .cert-thumbs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
    .cert-thumbs img{width:100%;height:210px;object-fit:contain;background:#fff;border:1px solid #e2e8f0;box-shadow:0 5px 14px rgba(15,23,42,.06)}
    @media(max-width:760px){.cert-trust{margin-top:30px;padding-top:22px}.cert-actions{display:grid;grid-template-columns:1fr;gap:10px}.cert-toggle{display:block}.cert-toggle summary{width:100%}.cert-view{width:100%;padding-top:14px}.cert-thumbs{grid-template-columns:1fr 1fr}.cert-thumbs img{height:190px}.cert-trust-people span{margin:0 6px}}
    @media(max-width:430px){.cert-thumbs img{height:165px}}
'''

if '/* CERT_TRUST_SECTION */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

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

p.write_text(s, encoding='utf-8')
