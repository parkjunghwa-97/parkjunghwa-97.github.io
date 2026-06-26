from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
p.write_text(s,encoding='utf-8')
