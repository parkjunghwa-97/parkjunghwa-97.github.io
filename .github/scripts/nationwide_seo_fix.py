from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old1 = '.review-shot img{display:block;height:520px;width:auto;max-width:none;object-fit:contain;border-radius:16px}'
new1 = '.review-shot img{display:block;width:320px;height:auto;max-height:520px;object-fit:contain;border-radius:16px}'
s = s.replace(old1, new1)

old2 = '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}'
new2 = '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{width:280px;height:auto;max-height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}'
s = s.replace(old2, new2)

old3 = '@media(max-width:430px){.review-shot img{height:390px}}'
new3 = '@media(max-width:430px){.review-shot img{width:250px;height:auto;max-height:390px}}'
s = s.replace(old3, new3)

p.write_text(s, encoding='utf-8')
