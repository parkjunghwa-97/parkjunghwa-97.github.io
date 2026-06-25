from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

TITLE = '기프트클린 대한청소만세 | 서울·경기·인천 입주청소 · 전국 특수청소'
DESCRIPTION = '서울·경기·인천 등 수도권 입주청소와 이사청소를 중심으로 상담합니다. 특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소 · 폐기물 처리 · 비둘기 퇴치 등 전국 출장 상담 가능.'
KEYWORDS = '서울 입주청소, 서울 이사청소, 경기 입주청소, 경기 이사청소, 인천 입주청소, 인천 이사청소, 부평 입주청소, 부평 이사청소, 송도 입주청소, 송도 이사청소, 청라 입주청소, 청라 이사청소, 검단 입주청소, 검단 이사청소, 계양 입주청소, 구월동 입주청소, 수원 입주청소, 용인 입주청소, 성남 입주청소, 고양 입주청소, 부천 입주청소, 화성 입주청소, 평택 입주청소, 김포 입주청소, 파주 입주청소, 안산 입주청소, 시흥 입주청소, 서울 특수청소, 경기 특수청소, 인천 특수청소, 부산 특수청소, 대구 특수청소, 대전 특수청소, 광주 특수청소, 울산 특수청소, 세종 특수청소, 청주 특수청소, 천안 특수청소, 서울 유품정리, 경기 유품정리, 인천 유품정리, 서울 고독사청소, 경기 고독사청소, 인천 고독사청소, 서울 쓰레기집 청소, 경기 쓰레기집 청소, 인천 쓰레기집 청소, 서울 폐기물 처리, 경기 폐기물 처리, 인천 폐기물 처리, 서울 비둘기 퇴치, 경기 비둘기 퇴치, 인천 비둘기 퇴치, 기프트클린, 대한청소만세, 기프트클린 대한청소만세'
SERVICE_COPY = '''서울·경기·인천 등 수도권 입주청소와 이사청소를 중심으로 상담합니다.

특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소 · 폐기물 처리 · 비둘기 퇴치 등<br>전국 출장 상담 가능.

사진 상담으로 현장 상태를 먼저 확인하고,<br>작업 범위와 예상 견적을 안내해드립니다.'''

s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESCRIPTION}">', s, count=1)
s = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{KEYWORDS}">', s, count=1)
s = re.sub(r'(<section id="service" class="page">.*?<h2>서비스 안내</h2>\s*)<p class="sub">.*?</p>', r'\1<p class="sub">' + SERVICE_COPY + r'</p>', s, count=1, flags=re.S)

# keep review slider clean: remove blank/duplicate images if any old lines come back
s = re.sub(r'\s*<div class="review-shot"><img src="images/reviews/review-(01|04)\.jpg" alt="[^"]+"></div>\n', '\n', s)

p.write_text(s, encoding='utf-8')
