from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'\s*<a href="/cases/new-apartment-checklist.html">.*?</a></div>\s*','\n',s,flags=re.S)
s=re.sub(r'(<div class="faq-grid">)\s*<div class="faq-card">.*?</div></details>',r'\1\n',s,count=1,flags=re.S)
s=s.replace('\uc815\ubc00 \uc810\uac80\uc740 \uc544\ub2c8\uc9c0\ub9cc, ','')
s=s.replace('\uc815\ubc00 \ud558\uc790\uc9c4\ub2e8\uc740 \uc544\ub2c8\uc9c0\ub9cc, ','')
p.write_text(s,encoding='utf-8')
