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

# Visible service copy
s = re.sub(r'(<section id="service" class="page">.*?<h2>서비스 안내</h2>\s*)<p class="sub">.*?</p>', r'\1<p class="sub">' + SERVICE_COPY + r'</p>', s, count=1, flags=re.S)

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
