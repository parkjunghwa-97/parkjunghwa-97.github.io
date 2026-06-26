from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = re.sub(r'(· 쓰레기집 청소)(?: · 쓰레기집 청소)+', r'\1', s)
s = s.replace('폐기물 처리 비용 안내', '폐기물 처리')
s = s.replace('작업 범위는 상담 기준으로 진행돼요를 확인해 예상 견적을 안내드립니다.', '작업 범위를 확인해 예상 견적을 안내드립니다.')
s = s.replace('<b>사업장 기준</b>', '<b>사업장</b>')

footer_local = '<div class="footer-local"><b>주요 서비스 지역</b><p>서울 · 경기 · 인천 / 부평 · 부천 · 송도 · 청라 · 검단 · 계양 · 수원 · 용인 · 성남 · 고양 · 김포 · 파주 · 안산 · 시흥 · 화성 · 평택</p><p>전국 출장 상담 가능 서비스: 특수청소 · 유품정리 · 정리 청소 · 폐기물 처리 등</p></div>'
s = re.sub(r'\s*<div class="footer-local".*?</div>\s*', '\n', s, flags=re.S)
s = s.replace('<div class="company-info">', footer_local + '\n<div class="company-info">', 1)

css = '/* FOOTER_LOCAL_TEXT */.footer-local{max-width:900px;margin:0 auto 18px;padding:18px;border-radius:22px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);color:#e5e7eb;line-height:1.7}.footer-local b{display:block;color:#fff;margin-bottom:8px}.footer-local p{margin:6px 0;color:#cbd5e1;font-size:14px}'
s = re.sub(r'\n\s*/\* FOOTER_LOCAL_TEXT \*/.*?(?=\n\s*</style>)', '\n', s, flags=re.S)
s = s.replace('</style>', css + '</style>', 1)

p.write_text(s, encoding='utf-8')
