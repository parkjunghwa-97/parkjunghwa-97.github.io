from pathlib import Path
import re
p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '<button class="nav-btn" onclick="showPage(\'contact\')">상담문의</button>'
new = '<button class="nav-btn" onclick="location.href=\'partner.html\'">파트너모집</button>\n      ' + old
if 'partner.html' not in s:
    s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
