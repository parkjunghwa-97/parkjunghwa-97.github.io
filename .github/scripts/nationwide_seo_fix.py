from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

card = '<div class="movein-check"><b>\uc2e0\ucd95 \uc785\uc8fc \uc804\ud6c4 \ud655\uc778\ud558\uba74 \uc88b\uc740 \uccb4\ud06c\ub9ac\uc2a4\ud2b8</b><p>\uc815\ubc00 \uc810\uac80\uc740 \uc544\ub2c8\uc9c0\ub9cc, \uc785\uc8fc\uccad\uc18c \uacfc\uc815\uc5d0\uc11c \ub208\uc5d0 \ub744\ub294 \ub9c8\uac10 \uc0c1\ud0dc\uc640 \uc0dd\ud65c \uccb4\ud06c \ud3ec\uc778\ud2b8\ub97c \ud568\uaed8 \ud655\uc778\ud569\ub2c8\ub2e4.</p><div><span>\ucc3d\ud2c0\xb7\uc0f7\uc2dc</span><span>\uc2f1\ud06c\ub300 \ud558\ubd80</span><span>\uc695\uc2e4 \ubc30\uc218</span><span>\ubb38\ud2c0\xb7\ubab0\ub529</span><span>\uc218\ub0a9\uc7a5 \ub0b4\ubd80</span><span>\ubc14\ub2e5 \ucc0d\ud798</span></div><a href="/cases/new-apartment-checklist.html">30\uac00\uc9c0 \uccb4\ud06c\ub9ac\uc2a4\ud2b8 \ubcf4\uae30</a></div>'

s = re.sub(r'\s*<div class="movein-check".*?</div>\s*', '\n', s, flags=re.S)
anchor = '<div class="service-area" aria-label="서비스 가능 지역 안내">'
if anchor in s:
    s = s.replace(anchor, card + '\n' + anchor, 1)

faq = '<div class="faq-card"><b>\uc785\uc8fc\uccad\uc18c\ud560 \ub54c \ud558\uc790\ub3c4 \uac19\uc774 \ud655\uc778\ud574\uc8fc\uc2dc\ub098\uc694?</b><p>\uc815\ubc00 \ud558\uc790\uc9c4\ub2e8\uc740 \uc544\ub2c8\uc9c0\ub9cc, \uccad\uc18c \uacfc\uc815\uc5d0\uc11c \ub208\uc5d0 \ub744\ub294 \ub9c8\uac10 \uc0c1\ud0dc\ub098 \uc0dd\ud65c \ud558\uc790 \uac00\ub2a5 \ubd80\ubd84\uc740 \ud568\uaed8 \ud655\uc778\ud574\ub4dc\ub9bd\ub2c8\ub2e4.</p></div>'
s = re.sub(r'\s*<div class="faq-card"><b>.*?\ud558\uc790.*?</div>', '', s, flags=re.S)
if '<div class="faq-grid">' in s and faq not in s:
    s = s.replace('<div class="faq-grid">', '<div class="faq-grid">\n        ' + faq, 1)

css = '/* MOVEIN_CHECK */.movein-check{margin:34px auto 0;max-width:820px;text-align:left;background:#fff;border:1px solid #e2e8f0;border-radius:28px;padding:28px;box-shadow:0 12px 34px rgba(15,23,42,.08)}.movein-check b{display:block;font-size:25px;color:#0f172a;margin-bottom:10px}.movein-check p{color:#475569;line-height:1.8}.movein-check div{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.movein-check span{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:999px;padding:10px;text-align:center;font-weight:900}.movein-check a{display:inline-flex;margin-top:18px;border-radius:999px;background:#0f172a;color:#fff;padding:12px 18px;font-weight:950}@media(max-width:760px){.movein-check{padding:22px}.movein-check div{grid-template-columns:1fr 1fr}}'
s = re.sub(r'\n\s*/\* MOVEIN_CHECK \*/.*?(?=\n\s*</style>)', '\n', s, flags=re.S)
s = s.replace('</style>', css + '</style>', 1)

p.write_text(s, encoding='utf-8')
