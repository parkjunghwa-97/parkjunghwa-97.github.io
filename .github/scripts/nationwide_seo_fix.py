from pathlib import Path
import re, json

p = Path('index.html')
s = p.read_text(encoding='utf-8')

TITLE = '기프트클린 대한청소만세 | 서울·경기·인천 입주청소 · 전국 특수청소'
DESCRIPTION = '서울·경기·인천 등 수도권 입주청소 · 이사청소, 특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소 · 폐기물 처리 · 비둘기 퇴치 전국 출장 상담 가능.'
KEYWORDS = '서울 입주청소, 서울 이사청소, 경기 입주청소, 경기 이사청소, 인천 입주청소, 인천 이사청소, 부평 입주청소, 부평 이사청소, 송도 입주청소, 송도 이사청소, 청라 입주청소, 청라 이사청소, 검단 입주청소, 검단 이사청소, 계양 입주청소, 구월동 입주청소, 수원 입주청소, 용인 입주청소, 성남 입주청소, 고양 입주청소, 부천 입주청소, 화성 입주청소, 평택 입주청소, 김포 입주청소, 파주 입주청소, 안산 입주청소, 시흥 입주청소, 서울 특수청소, 경기 특수청소, 인천 특수청소, 부산 특수청소, 대구 특수청소, 대전 특수청소, 광주 특수청소, 울산 특수청소, 세종 특수청소, 청주 특수청소, 천안 특수청소, 서울 유품정리, 경기 유품정리, 인천 유품정리, 서울 고독사청소, 경기 고독사청소, 인천 고독사청소, 서울 쓰레기집 청소, 경기 쓰레기집 청소, 인천 쓰레기집 청소, 서울 폐기물 처리, 경기 폐기물 처리, 인천 폐기물 처리, 서울 비둘기 퇴치, 경기 비둘기 퇴치, 인천 비둘기 퇴치, 기프트클린, 대한청소만세, 기프트클린 대한청소만세'
SERVICE_COPY = '''서울·경기·인천 등 수도권 입주청소 · 이사청소

특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소 · 폐기물 처리 · 비둘기 퇴치<br>전국 출장 상담 가능.

사진 상담으로 현장 상태를 먼저 확인하고,<br>작업 범위와 예상 견적을 안내해드립니다.'''
TRUST_STYLE = '''
    .trust-box{margin:22px 0 28px;padding:26px;border-radius:26px;background:#0f172a;color:#fff;box-shadow:0 12px 30px rgba(15,23,42,.18);line-height:1.75;text-align:left}
    .trust-box b{display:block;font-size:23px;line-height:1.45;margin-bottom:14px;color:#fff}
    .trust-box p{margin:0;color:#e5e7eb;font-size:16px;line-height:1.8}
    .trust-box .trust-note{margin-top:12px;color:#fff;font-weight:900}
    @media(max-width:760px){.trust-box{padding:22px;border-radius:22px}.trust-box b{font-size:20px}.trust-box p{font-size:15px}}
'''
TRUST_BOX = '''<div class="trust-box">
        <b>낮은 견적보다 중요한 건,<br>작업 전 정확한 안내입니다.</b>
        <p>현장에서 금액이 달라질 수 있는 부분,<br>추가 작업이 필요한 상황을 먼저 설명합니다.</p>
        <p class="trust-note">동의 없는 추가 작업은 진행하지 않습니다.</p>
      </div>

      '''
DEPOSIT_STYLE = '''
    .deposit-box{margin:0 0 20px;padding:18px;border-radius:20px;background:#f8fafc;border:1px solid #e2e8f0;line-height:1.7}
    .deposit-box b{display:block;margin-bottom:8px;font-size:17px;color:#0f172a}
    .deposit-box p{margin:0 0 14px;color:#64748b;font-size:14.5px}
    .deposit-btn{display:inline-flex;align-items:center;justify-content:center;padding:12px 18px;border-radius:999px;background:#0f172a;color:#fff;font-weight:900;font-size:14px;box-shadow:0 8px 18px rgba(15,23,42,.16)}
'''
DEPOSIT_BOX = '''<div class="deposit-box">
          <b>예약금 안내</b>
          <p>상담 후 일정이 확정되면 예약금 안내가 진행됩니다.<br>예약금은 최종 결제 금액에서 차감됩니다.</p>
          <a class="deposit-btn" href="https://pf.kakao.com/_lxhwGX" target="_blank">예약금 안내 받기</a>
        </div>

        '''

# Basic meta
s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESCRIPTION}">', s, count=1)
s = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{KEYWORDS}">', s, count=1)

# Remove outdated single-city geo meta tags. Service area is handled in JSON-LD areaServed.
s = re.sub(r'\n\s*<meta name="geo\.region" content="[^"]*">', '', s)
s = re.sub(r'\n\s*<meta name="geo\.placename" content="[^"]*">', '', s)
s = re.sub(r'\n\s*<meta name="geo\.position" content="[^"]*">', '', s)
s = re.sub(r'\n\s*<meta name="ICBM" content="[^"]*">', '', s)

# OpenGraph / Twitter
s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE}">', s, count=1)
s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESCRIPTION}">', s, count=1)
s = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{TITLE}">', s, count=1)
s = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{DESCRIPTION}">', s, count=1)

# Visible service copy and trust message
s = re.sub(r'(<section id="service" class="page">.*?<h2>서비스 안내</h2>\s*)<p class="sub">.*?</p>', r'\1<p class="sub">' + SERVICE_COPY + r'</p>', s, count=1, flags=re.S)
s = re.sub(r'\s*<div class="trust-box">.*?</div>\s*', '\n', s, count=0, flags=re.S)
s = re.sub(r'(<section id="service" class="page">.*?<p class="sub">.*?</p>\s*)', r'\1' + TRUST_BOX, s, count=1, flags=re.S)
if '.trust-box{' not in s:
    s = s.replace('\n  </style>', TRUST_STYLE + '\n  </style>', 1)

# Reservation deposit guide UI
if '.deposit-box{' not in s:
    s = s.replace('\n  </style>', DEPOSIT_STYLE + '\n  </style>', 1)
s = re.sub(r'(<div class="form-card">\s*<h3>상담 예약하기</h3>\s*<p>.*?</p>\s*)(?:<div class="deposit-box">.*?</div>\s*)?(<form class="contact-form")', r'\1' + DEPOSIT_BOX + r'\2', s, count=1, flags=re.S)

# JSON-LD GEO/AI-readable service area
m = re.search(r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)', s, flags=re.S)
if m:
    data = json.loads(m.group(2))
    for item in data.get('@graph', []):
        if item.get('@type') == 'WebSite':
            item['description'] = DESCRIPTION
        t = item.get('@type')
        if (isinstance(t, list) and 'LocalBusiness' in t) or t == 'LocalBusiness':
            item['description'] = DESCRIPTION
            item['areaServed'] = [
                {'@type': 'AdministrativeArea', 'name': '서울특별시'},
                {'@type': 'AdministrativeArea', 'name': '경기도'},
                {'@type': 'AdministrativeArea', 'name': '인천광역시'},
                {'@type': 'City', 'name': '부평'},
                {'@type': 'City', 'name': '송도'},
                {'@type': 'City', 'name': '청라'},
                {'@type': 'City', 'name': '검단'},
                {'@type': 'AdministrativeArea', 'name': '부산광역시'},
                {'@type': 'AdministrativeArea', 'name': '대구광역시'},
                {'@type': 'AdministrativeArea', 'name': '대전광역시'},
                {'@type': 'AdministrativeArea', 'name': '광주광역시'},
                {'@type': 'AdministrativeArea', 'name': '울산광역시'},
                {'@type': 'AdministrativeArea', 'name': '세종특별자치시'},
                {'@type': 'AdministrativeArea', 'name': '충청권'},
                {'@type': 'Country', 'name': '대한민국'}
            ]
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    s = s[:m.start()] + m.group(1) + '\n' + new_json + '\n' + m.group(3) + s[m.end():]

# keep review slider clean
s = re.sub(r'\s*<div class="review-shot"><img src="images/reviews/review-(01|04)\.jpg" alt="[^"]+"></div>\n', '\n', s)

p.write_text(s, encoding='utf-8')
