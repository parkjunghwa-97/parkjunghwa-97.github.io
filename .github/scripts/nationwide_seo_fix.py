from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# remove movein checklist block
start=s.find('<div class="movein-check"')
if start!=-1:
    end=s.find('<div class="service-area"', start)
    if end!=-1:
        s=s[:start]+s[end:]
# remove movein css block
mark='/* MOVEIN_CHECK */'
start=s.find(mark)
if start!=-1:
    end=s.find('</style>', start)
    if end!=-1:
        s=s[:start]+s[end:]
# remove bad faq insert before details
marker='<div class="faq-grid">'
start=s.find(marker)
if start!=-1:
    end=s.find('<details><summary>', start)
    if end!=-1 and 'faq-card' in s[start:end]:
        s=s[:start+len(marker)]+'\n        '+s[end:]
p.write_text(s, encoding='utf-8')
