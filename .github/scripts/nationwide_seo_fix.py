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

circle_bar = '''    .fixed-contact-bar{position:fixed;right:20px;bottom:92px;z-index:999;display:flex;flex-direction:column;gap:10px;background:transparent;padding:0;border-radius:0;box-shadow:none;width:auto}
    .fixed-contact-bar a{display:flex;align-items:center;justify-content:center;text-align:center;width:76px;height:76px;border-radius:50%;padding:0;background:#fff;color:#0f172a;font-weight:950;font-size:13px;line-height:1.22;text-decoration:none;box-shadow:0 10px 24px rgba(0,0,0,.18);border:1px solid rgba(15,23,42,.16);word-spacing:999px}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a;border-color:rgba(202,138,4,.22)}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:88px;gap:8px}.fixed-contact-bar a{width:68px;height:68px;font-size:12px;line-height:1.18}footer{padding-bottom:170px}.fixed-call{display:none}}'''

old1 = '''    .fixed-contact-bar{position:fixed;right:16px;bottom:82px;z-index:999;display:flex;flex-direction:column;gap:8px;background:rgba(15,23,42,.94);padding:9px;border-radius:22px;box-shadow:0 12px 30px rgba(0,0,0,.25);backdrop-filter:blur(8px);width:150px}
    .fixed-contact-bar a{text-align:center;border-radius:999px;padding:12px 10px;background:#fff;color:#0f172a;font-weight:950;font-size:14px;text-decoration:none}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:76px;width:142px}.fixed-contact-bar a{font-size:14px;padding:12px 8px}footer{padding-bottom:170px}.fixed-call{display:none}}'''
old2 = '''    .fixed-contact-bar{position:fixed;right:18px;bottom:88px;z-index:999;display:flex;flex-direction:column;gap:10px;background:transparent;padding:0;border-radius:0;box-shadow:none;width:142px}
    .fixed-contact-bar a{text-align:center;border-radius:999px;padding:13px 10px;background:#fff;color:#0f172a;font-weight:950;font-size:14px;text-decoration:none;box-shadow:0 10px 24px rgba(0,0,0,.18);border:1px solid rgba(15,23,42,.16)}
    .fixed-contact-bar a.kakao{background:#facc15;color:#0f172a;border-color:rgba(202,138,4,.22)}
    @media(max-width:760px){.fixed-contact-bar{right:12px;bottom:84px;width:132px;gap:8px}.fixed-contact-bar a{font-size:13.5px;padding:12px 8px}footer{padding-bottom:170px}.fixed-call{display:none}}'''

s = s.replace(old1, circle_bar)
s = s.replace(old2, circle_bar)

p.write_text(s, encoding='utf-8')
