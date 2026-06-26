from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the temporary mobile popup style/action.
s = s.replace('''

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
''', '\n')

# Stronger slider and lightbox CSS.
css = '''

    /* MOBILE_ABOUT_SAME_ACTION */
    @media(max-width:760px){.fly-about-text{z-index:999999!important;color:#0f172a!important;text-shadow:0 8px 28px rgba(255,255,255,.98),0 2px 10px rgba(255,255,255,.95)}}

    /* SLIDER_DRAG_ZOOM_FIX */
    .grab-slider{overflow-x:auto!important;overflow-y:hidden!important;cursor:grab!important;-webkit-overflow-scrolling:touch;scrollbar-width:none;touch-action:pan-x;user-select:none}
    .grab-slider::-webkit-scrollbar{display:none}
    .grab-slider.is-dragging{cursor:grabbing!important}
    .grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important;width:max-content!important}
    .grab-slider img{cursor:zoom-in!important;user-select:none!important;-webkit-user-drag:none!important}
    .image-lightbox{position:fixed;inset:0;background:rgba(15,23,42,.9);z-index:999999;display:none;align-items:center;justify-content:center;padding:18px}
    .image-lightbox.open{display:flex!important}
    .image-lightbox img{max-width:94vw;max-height:88vh;object-fit:contain;background:#fff;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.38)}
    .image-lightbox button{position:fixed;top:14px;right:14px;border:0;background:white;color:#0f172a;border-radius:999px;width:42px;height:42px;font-size:24px;font-weight:900;cursor:pointer}
'''
if '/* MOBILE_ABOUT_SAME_ACTION */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

# Restore the same flying action on mobile instead of the popup card.
old = '''      if(window.innerWidth <= 760){
        section.classList.remove('prep');
        targetText.style.visibility='visible';
        targetText.classList.remove('mobile-burst');
        void targetText.offsetWidth;
        targetText.classList.add('mobile-burst');
        return;
      }

      section.classList.add('prep');
      targetText.style.visibility='hidden';'''
new = '''      section.classList.add('prep');
      targetText.style.visibility='hidden';'''
s = s.replace(old, new, 1)

# Make mobile flight start lower and last a little longer.
s = s.replace("const startTop=isMobile ? '39vh' : '50vh';", "const startTop=isMobile ? '45vh' : '50vh';")
s = s.replace("const startFont=isMobile ? '36px' : '80px';", "const startFont=isMobile ? '38px' : '80px';")
s = s.replace("const duration=isMobile ? 1250 : 950;", "const duration=isMobile ? 1500 : 950;")
s = s.replace("setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 160 : 40);", "setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);")

# Include review screenshot slider in the grab/zoom initializer.
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")
s = s.replace(".grab-slider .case-strip,.grab-slider .cert-marquee-track", ".grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track")

p.write_text(s, encoding='utf-8')
