from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = re.sub(r'(· 쓰레기집 청소)(?: · 쓰레기집 청소)+', r'\1', s)
s = s.replace('폐기물 처리 비용 안내', '폐기물 처리')
s = s.replace('작업 범위는 상담 기준으로 진행돼요를 확인해 예상 견적을 안내드립니다.', '작업 범위를 확인해 예상 견적을 안내드립니다.')
s = s.replace('<b>사업장 기준</b>', '<b>사업장</b>')
p.write_text(s, encoding='utf-8')
