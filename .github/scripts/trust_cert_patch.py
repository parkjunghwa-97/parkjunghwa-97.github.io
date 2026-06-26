from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css = '''

    /* MOBILE_ABOUT_REVIEW_FIX */
    @media(max-width:760px){
      .about-highlight.mobile-burst{display:block!important;visibility:visible!important;text-align:center!important;font-size:28px!important;font-weight:950!important;color:#0f172a!important;line-height:1.35!important;margin:28px auto!important;padding:18px 12px!important;border-radius:22px!important;background:rgba(255,255,255,.92)!important;box-shadow:0 14px 34px rgba(15,23,42,.10)!important;animation:mobileBurst 1.15s cubic-bezier(.16,1,.3,1) both!important}
      @keyframes mobileBurst{0%{opacity:0;transform:scale(.78) translateY(18px)}35%{opacity:1;transform:scale(1.08) translateY(0)}100%{opacity:1;transform:scale(1) translateY(0)}}
      .about-page.prep .about-content{opacity:1!important}
    }
    .grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important}
    .review-marquee.grab-slider{overflow-x:auto!important;overflow-y:hidden!important;-webkit-overflow-scrolling:touch;scrollbar-width:none;touch-action:pan-x;cursor:grab!important}
    .review-marquee.grab-slider::-webkit-scrollbar{display:none}
    .review-marquee.grab-slider .review-track{width:max-content!important}
    .review-marquee.grab-slider img{cursor:zoom-in!important;user-select:none!important;-webkit-user-drag:none!important}
'''
if '/* MOBILE_ABOUT_REVIEW_FIX */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

needle = """      section.classList.add('prep');
      targetText.style.visibility='hidden';"""
replacement = """      if(window.innerWidth <= 760){
        section.classList.remove('prep');
        targetText.style.visibility='visible';
        targetText.classList.remove('mobile-burst');
        void targetText.offsetWidth;
        targetText.classList.add('mobile-burst');
        return;
      }

      section.classList.add('prep');
      targetText.style.visibility='hidden';"""
if 'mobile-burst' not in s.split('function playAboutLanding(section){', 1)[-1].split('document.addEventListener', 1)[0]:
    s = s.replace(needle, replacement, 1)

s = s.replace(".grab-slider .case-strip,.grab-slider .cert-marquee-track", ".grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track")
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")

p.write_text(s, encoding='utf-8')
