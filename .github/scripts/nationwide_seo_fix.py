from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

bad = '<div class="review-shot"><img src="images/reviews/review-03.jpg" alt="고객 후기 3"></div>'
s = s.replace(bad, '')

s = s.replace('전국 특수청소 · 유품정리 · 고독사청소', '전국 특수청소 · 유품정리 · 고독사청소 · 쓰레기집 청소')

s = s.replace(
    '.intro-logo{width:300px;max-width:80vw;object-fit:contain;margin-bottom:16px;filter:drop-shadow(0 12px 28px rgba(0,0,0,.45));animation:fadeUp .7s ease forwards}',
    '.intro-logo{width:250px;max-width:68vw;object-fit:contain;margin-bottom:14px;filter:drop-shadow(0 12px 28px rgba(0,0,0,.45));animation:fadeUp .7s ease forwards}'
)

intro_mobile = '    @media(max-width:760px){.intro-logo{width:180px;max-width:56vw;margin-bottom:12px}.intro-main{font-size:24px}.intro-sub{font-size:14px;margin-top:14px;line-height:1.7}}\n'
if 'intro-logo{width:180px' not in s:
    s = s.replace('    @keyframes fadeUp', intro_mobile + '    @keyframes fadeUp', 1)

s = s.replace(
    '.review-shot img{display:block;height:520px;width:auto;max-width:none;object-fit:contain;border-radius:16px}',
    '.review-shot img{display:block;width:320px;height:auto;max-height:520px;object-fit:contain;border-radius:16px}'
)
s = s.replace(
    '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}',
    '@media(max-width:760px){.review-track{gap:14px;animation-duration:50s}.review-shot{padding:10px;border-radius:18px}.review-shot img{width:280px;height:auto;max-height:430px;border-radius:14px}.review-marquee:before,.review-marquee:after{width:30px}.faq-grid{grid-template-columns:1fr}.faq-card{padding:20px}}'
)
s = s.replace(
    '@media(max-width:430px){.review-shot img{height:390px}}',
    '@media(max-width:430px){.review-shot img{width:250px;height:auto;max-height:390px}}'
)

p.write_text(s, encoding='utf-8')
