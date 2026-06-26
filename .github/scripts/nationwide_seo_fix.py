from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 기본 문구 정리
s = s.replace('<div class="review-shot"><img src="images/reviews/review-03.jpg" alt="고객 후기 3"></div>', '')
s = s.replace('전국 특수청소 · 유품정리 · 고독사청소', '전국 특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소')
s = s.replace('폐기물 처리 비용 안내', '폐기물 처리')
s = s.replace('작업 범위는 상담 기준으로 진행돼요를 확인해 예상 견적을 안내드립니다.', '작업 범위를 확인해 예상 견적을 안내드립니다.')
s = s.replace('<b>사업장 기준</b>', '<b>사업장</b>')

# 인트로 로고 축소
s = s.replace(
    '.intro-logo{width:300px;max-width:80vw;object-fit:contain;margin-bottom:16px;filter:drop-shadow(0 12px 28px rgba(0,0,0,.45));animation:fadeUp .7s ease forwards}',
    '.intro-logo{width:250px;max-width:68vw;object-fit:contain;margin-bottom:14px;filter:drop-shadow(0 12px 28px rgba(0,0,0,.45));animation:fadeUp .7s ease forwards}'
)
if 'intro-logo{width:180px' not in s:
    s = s.replace('    @keyframes fadeUp', '    @media(max-width:760px){.intro-logo{width:180px;max-width:56vw;margin-bottom:12px}.intro-main{font-size:24px}.intro-sub{font-size:14px;margin-top:14px;line-height:1.7}}\n    @keyframes fadeUp', 1)

# 후기 이미지 크기 정리
s = s.replace(
    '.review-shot img{display:block;height:520px;width:auto;max-width:none;object-fit:contain;border-radius:16px}',
    '.review-shot img{display:block;width:320px;height:auto;max-height:520px;object-fit:contain;border-radius:16px}'
)
s = s.replace(
    '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}',
    '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{width:280px;height:auto;max-height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}'
)
s = s.replace('@media(max-width:430px){.review-shot img{height:390px}}', '@media(max-width:430px){.review-shot img{width:250px;height:auto;max-height:390px}}')

schema_json = '''  <!-- SCHEMA_ORG_JSONLD -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "LocalBusiness",
        "@id": "https://parkjunghwa-97.github.io/#business",
        "name": "기프트클린 대한청소만세",
        "alternateName": ["대한청소만세", "기프트클린"],
        "url": "https://parkjunghwa-97.github.io/",
        "telephone": "+82-10-4122-9207",
        "address": {
          "@type": "PostalAddress",
          "streetAddress": "부영로 165",
          "addressLocality": "부평구",
          "addressRegion": "인천광역시",
          "addressCountry": "KR"
        },
        "image": "https://parkjunghwa-97.github.io/logo.png",
        "priceRange": "현장 상태에 따라 상담 후 안내",
        "description": "서울·경기·인천 입주청소와 이사청소, 전국 특수청소·고독사청소·유품정리·쓰레기집 청소·폐기물 처리·비둘기 퇴치 상담.",
        "areaServed": ["서울", "경기", "인천", "대전", "세종", "충청", "강원", "부산", "대구", "울산", "광주", "전라", "경상"],
        "serviceArea": ["서울", "경기", "인천", "전국 출장 상담 가능 서비스"],
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
        "sameAs": ["https://pf.kakao.com/_lxhwGX"]
      },
      {
        "@type": "WebSite",
        "@id": "https://parkjunghwa-97.github.io/#website",
        "url": "https://parkjunghwa-97.github.io/",
        "name": "기프트클린 대한청소만세",
        "publisher": {"@id": "https://parkjunghwa-97.github.io/#business"}
      },
      {
        "@type": "FAQPage",
        "@id": "https://parkjunghwa-97.github.io/#faq",
        "mainEntity": [
          {"@type":"Question","name":"사진만 보내도 견적 가능한가요?","acceptedAnswer":{"@type":"Answer","text":"네, 가능합니다. 현장 사진이나 영상을 보내주시면 오염도, 짐 유무, 폐기물 양, 작업 범위를 확인해 예상 견적을 안내드립니다. 다만 사진에 보이지 않는 오염이나 추가 작업이 있는 경우 현장에서 금액이 변동될 수 있습니다."}},
          {"@type":"Question","name":"당일 청소도 가능한가요?","acceptedAnswer":{"@type":"Answer","text":"일정이 맞는 경우 당일 작업도 가능합니다. 작업 종류, 현장 상태, 이동 거리, 투입 인원에 따라 가능 여부가 달라질 수 있어 상담 시 확인이 필요합니다."}},
          {"@type":"Question","name":"입주청소와 이사청소는 다른가요?","acceptedAnswer":{"@type":"Answer","text":"입주청소는 새로 들어가기 전 빈 공간을 기준으로 진행하는 경우가 많고, 이사청소는 이전 거주 흔적이나 생활 오염이 남아 있는 경우가 많습니다. 현장 상태에 따라 작업 범위와 비용이 달라질 수 있습니다."}},
          {"@type":"Question","name":"쓰레기집 청소도 가능한가요?","acceptedAnswer":{"@type":"Answer","text":"네, 가능합니다. 생활쓰레기, 음식물 쓰레기, 악취, 바닥 오염, 폐기물 양을 확인한 뒤 작업 범위와 예상 비용을 안내드립니다. 사진 확인 후 예상 견적 안내가 가능합니다."}},
          {"@type":"Question","name":"비둘기 퇴치는 어떤 작업을 하나요?","acceptedAnswer":{"@type":"Answer","text":"현장 상태에 따라 분변 제거, 둥지 제거, 알·새끼 확인, 유입경로 차단막 설치 등을 진행합니다. 스카이 장비나 외부 작업이 필요한 경우 별도 안내드립니다."}},
          {"@type":"Question","name":"추가 비용은 언제 발생하나요?","acceptedAnswer":{"@type":"Answer","text":"상담 당시 확인되지 않은 심한 오염, 폐기물 증가, 추가 공간, 추가 작업 요청, 장비 사용, 유료 주차비 등이 있는 경우 추가 비용이 발생할 수 있습니다. 추가 작업은 사전 안내 후 진행됩니다."}},
          {"@type":"Question","name":"작업 후 A/S는 가능한가요?","acceptedAnswer":{"@type":"Answer","text":"작업 완료 후 3일 이내 접수 가능합니다. 사진 또는 영상으로 확인 후 작업 범위 내 미흡한 부분인지 확인하여 안내드립니다. 작업 완료 후 새로 발생한 오염이나 사용 중 발생한 오염은 A/S 대상에서 제외될 수 있습니다."}}
        ]
      }
    ]
  }
  </script>
'''
s = re.sub(r'\n\s*<!-- SCHEMA_ORG_JSONLD -->\s*<script type="application/ld\+json">.*?</script>\s*', '\n', s, flags=re.S)
font_link = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">'
if font_link in s:
    s = s.replace(font_link, schema_json + '  ' + font_link, 1)

process_html = '''      <div class="process flow-process" aria-label="상담부터 작업까지 진행 절차">
        <div class="flow-step t1"><span>01</span><b>문의 상담</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t2"><span>02</span><b>사진·영상 접수</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t3"><span>03</span><b>현장 상태 확인</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t4"><span>04</span><b>예상 견적·예약금 안내</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t5"><span>05</span><b>예약금 확인 후 예약 확정</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t6"><span>06</span><b>안내사항 발송 후 작업 진행</b></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step t7"><span>07</span><b>작업 완료 후 확인</b></div>
      </div>'''
s = re.sub(r'      <div class="process(?: flow-process)?"[^>]*>.*?\n      </div>', process_html, s, count=1, flags=re.S)

process_css = '''
    /* PROCESS_FLOW_SECTION */
    .flow-process{display:flex;align-items:center;justify-content:center;gap:12px;margin:34px auto 10px;flex-wrap:nowrap;overflow-x:auto;padding:10px 4px 18px;scrollbar-width:none}
    .flow-process::-webkit-scrollbar{display:none}
    .flow-step{flex:0 0 108px;width:108px;height:108px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:0 10px 26px rgba(15,23,42,.08);border:1px solid #e2e8f0;padding:12px;color:#0f172a;transition:.2s ease}
    .flow-step span{display:block;font-size:11px;font-weight:950;margin-bottom:5px;letter-spacing:.03em;color:inherit;opacity:.78}
    .flow-step b{display:block;font-size:12.2px;line-height:1.3;font-weight:950;word-break:keep-all;color:inherit}
    .flow-step.t1{background:#ffffff}.flow-step.t2{background:#f8fafc}.flow-step.t3{background:#f1f5f9}.flow-step.t4{background:#e2e8f0}.flow-step.t5{background:#cbd5e1;color:#0f172a;border-color:#cbd5e1}.flow-step.t6{background:#475569;color:#fff;border-color:#475569}.flow-step.t7{background:#0f172a;color:#fff;border-color:#0f172a;box-shadow:0 14px 32px rgba(15,23,42,.22)}
    .flow-arrow{flex:0 0 auto;color:#94a3b8;font-size:22px;font-weight:900}
    @media(max-width:760px){.flow-process{justify-content:flex-start;gap:9px;margin-top:28px;padding-bottom:16px}.flow-step{flex-basis:92px;width:92px;height:92px;padding:9px}.flow-step b{font-size:11px}.flow-step span{font-size:10.5px;margin-bottom:4px}.flow-arrow{font-size:18px}}
'''
s = re.sub(r'\n\s*/\* PROCESS_FLOW_SECTION \*/.*?(?=\n\s*/\* SERVICE_AREA_SECTION \*/)', process_css, s, count=1, flags=re.S)
if 'PROCESS_FLOW_SECTION' not in s:
    s = s.replace('\n    /* SERVICE_AREA_SECTION */', process_css + '\n    /* SERVICE_AREA_SECTION */', 1)

area_html = '''

      <div class="service-area" aria-label="서비스 가능 지역 안내">
        <div class="area-kicker">서비스 가능 지역 안내</div>
        <h3>지역과 현장 상태를 확인한 뒤 안내드립니다</h3>
        <p class="area-lead">대한청소만세는 서울·경기·인천 등 수도권을 중심으로 입주청소와 이사청소를 상담하고 있습니다.</p>
        <p class="area-business"><b>사업장</b> 인천광역시 부평구 부영로 165</p>

        <div class="area-split">
          <div class="area-box"><b>입주청소 · 이사청소 가능 지역</b><p>서울 / 경기 / 인천</p></div>
          <div class="area-box strong"><b>전국 출장 상담 가능 서비스</b><p>특수청소 / 고독사청소 / 유품정리 / 쓰레기집 청소 / 폐기물 처리 / 비둘기 퇴치</p></div>
        </div>

        <div class="area-region"><b>주요 상담 지역</b><p>서울, 인천, 부천, 부평, 송도, 청라, 검단, 계양, 수원, 용인, 성남, 고양, 김포, 파주, 안산, 시흥, 화성, 평택, 대전, 세종, 충청, 강원, 부산, 대구, 울산, 광주, 전라, 경상 지역</p></div>
        <p class="area-note">지역별 가능 여부는 현장 상태, 일정, 작업 범위에 따라 달라질 수 있습니다.<br>사진이나 영상을 보내주시면 출장 가능 여부와 예상 견적을 먼저 안내드립니다.</p>
      </div>'''
s = re.sub(r'\n\s*<div class="service-area" aria-label="서비스 가능 지역 안내">.*?</div>\s*(?=\n\s*</div>\s*</section>\s*\n\s*<section id="portfolio")', '\n', s, count=1, flags=re.S)
if 'aria-label="서비스 가능 지역 안내"' not in s:
    s = s.replace(process_html, process_html + area_html, 1)

area_css = '''
    /* SERVICE_AREA_SECTION */
    .service-area{margin:34px auto 0;max-width:980px;text-align:left;background:linear-gradient(180deg,#ffffff,#f8fafc);border:1px solid rgba(226,232,240,.95);border-radius:30px;padding:30px;box-shadow:0 12px 34px rgba(15,23,42,.08)}
    .area-kicker{font-size:13px;font-weight:950;color:#64748b;letter-spacing:.02em;margin-bottom:8px}
    .service-area h3{margin:0 0 12px;font-size:28px;line-height:1.28;color:#0f172a}
    .area-lead{margin:0 0 12px;color:#475569;line-height:1.7;font-size:16px}
    .area-business{display:inline-flex;align-items:center;gap:8px;margin:0 0 20px;padding:10px 14px;border-radius:999px;background:#f1f5f9;border:1px solid #e2e8f0;color:#334155;font-size:14px;font-weight:800}
    .area-business b{color:#0f172a;font-weight:950}
    .area-split{display:grid;grid-template-columns:1fr 1.4fr;gap:14px;margin:18px 0}
    .area-box{background:#fff;border-radius:22px;padding:20px;border:1px solid #e2e8f0;box-shadow:0 8px 20px rgba(15,23,42,.05)}
    .area-box.strong{background:#0f172a;color:#fff;border-color:#0f172a}
    .area-box b{display:block;font-size:16px;margin-bottom:10px;color:inherit}
    .area-box p{margin:0;color:inherit;opacity:.88;line-height:1.7;font-weight:800}
    .area-region{margin-top:16px;background:#f1f5f9;border-radius:22px;padding:20px;border:1px solid #e2e8f0}.area-region b{display:block;margin-bottom:10px;color:#0f172a;font-size:16px}.area-region p{margin:0;color:#475569;line-height:1.9;font-size:15px}
    .area-note{margin:18px 0 0;padding-left:16px;border-left:4px solid #0f172a;color:#334155;line-height:1.75;font-weight:800}
    @media(max-width:760px){.service-area{padding:22px;border-radius:24px}.service-area h3{font-size:23px}.area-business{font-size:13px;line-height:1.45;border-radius:18px}.area-split{grid-template-columns:1fr}.area-region p{font-size:14.5px}.area-note{font-size:14.5px}}
'''
s = re.sub(r'\n\s*/\* SERVICE_AREA_SECTION \*/.*?(?=\n\s*/\* MOBILE_NAV_FLOW_FIX \*/)', area_css, s, count=1, flags=re.S)
if 'SERVICE_AREA_SECTION' not in s:
    s = s.replace('\n    /* MOBILE_NAV_FLOW_FIX */', area_css + '\n    /* MOBILE_NAV_FLOW_FIX */', 1)

circle_bar = '''    .fixed-contact-bar{position:fixed;right:20px;bottom:92px;z-index:999;display:flex;flex-direction:column;gap:10px;background:transparent;padding:0;border-radius:0;box-shadow:none;width:auto}
    .fixed-contact-bar a{display:flex;align-items:center;justify-content:center;text-align:center;width:76px;height:76px;border-radius:50%;padding:0;background:#fff;color:#0f172a;font-weight:950;font-size:13px;line-height:1.22;text-decoration:none;box-shadow:0 10px 24px rgba(0,0,0,.18);border:1px solid rgba(15,23,42,.16);word-spacing:999px}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a;border-color:rgba(202,138,4,.22)}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:88px;gap:8px}.fixed-contact-bar a{width:68px;height:68px;font-size:12px;line-height:1.18}footer{padding-bottom:170px}.fixed-call{display:none}}'''
for old in [
'''    .fixed-contact-bar{position:fixed;right:16px;bottom:82px;z-index:999;display:flex;flex-direction:column;gap:8px;background:rgba(15,23,42,.94);padding:9px;border-radius:22px;box-shadow:0 12px 30px rgba(0,0,0,.25);backdrop-filter:blur(8px);width:150px}
    .fixed-contact-bar a{text-align:center;border-radius:999px;padding:12px 10px;background:#fff;color:#0f172a;font-weight:950;font-size:14px;text-decoration:none}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:76px;width:142px}.fixed-contact-bar a{font-size:14px;padding:12px 8px}footer{padding-bottom:170px}.fixed-call{display:none}}''',
'''    .fixed-contact-bar{position:fixed;right:18px;bottom:88px;z-index:999;display:flex;flex-direction:column;gap:10px;background:transparent;padding:0;border-radius:0;box-shadow:none;width:142px}
    .fixed-contact-bar a{text-align:center;border-radius:999px;padding:13px 10px;background:#fff;color:#0f172a;font-weight:950;font-size:14px;text-decoration:none;box-shadow:0 10px 24px rgba(0,0,0,.18);border:1px solid rgba(15,23,42,.16)}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a;border-color:rgba(202,138,4,.22)}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:84px;width:132px;gap:8px}.fixed-contact-bar a{font-size:13.5px;padding:12px 8px}footer{padding-bottom:170px}.fixed-call{display:none}}''']:
    s = s.replace(old, circle_bar)

p.write_text(s, encoding='utf-8')
