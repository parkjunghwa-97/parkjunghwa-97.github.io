from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('      <p class="sub">예약, 환불, 작업 범위, A/S, 면책사항을 항목별로 확인하실 수 있습니다.</p>\n','')
p.write_text(s,encoding='utf-8')
