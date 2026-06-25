from pathlib import Path
import re
p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = re.sub(r'\s*<div class="review-shot"><img src="images/reviews/review-(01|04)\.jpg" alt="[^"]+"></div>\n', '\n', s)
p.write_text(s, encoding='utf-8')
