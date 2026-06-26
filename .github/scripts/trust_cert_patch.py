from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep slider animation moving while allowing drag.
s = s.replace("if(track){track.style.animation='none';}", "if(track){track.style.animationPlayState='running';}")
s = s.replace('.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important;width:max-content!important}',
              '.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{width:max-content!important}')
s = s.replace('.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important}',
              '.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{}')

# Include review screenshots in draggable sliders.
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")

# Re-init sliders when opening hidden sections.
old_init = """      function init(){
        document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);
      }
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}"""
new_init = """      window.initSliders=function(){
        document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);
      };
      function init(){window.initSliders();}
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}"""
s = s.replace(old_init, new_init, 1)
old_show = """      if(target && id === 'about'){
        setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);
      }"""
new_show = """      if(target && id === 'about'){
        setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);
      }
      if(window.initSliders){setTimeout(window.initSliders, 80);}"""
s = s.replace(old_show, new_show, 1)

# Make the lightbox CSS strong enough for desktop browser.
css = '''

    /* DESKTOP_SLIDER_ZOOM_FIX */
    .slider-lightbox{position:fixed!important;inset:0!important;background:rgba(15,23,42,.9)!important;z-index:9999999!important;display:none;align-items:center;justify-content:center;padding:18px}
    .slider-lightbox.open{display:flex!important}
    .slider-lightbox img{max-width:94vw;max-height:88vh;object-fit:contain;background:#fff;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.38)}
    .slider-lightbox button{position:fixed;top:14px;right:14px;border:0;background:#fff;color:#0f172a;border-radius:999px;width:42px;height:42px;font-size:24px;font-weight:900;cursor:pointer}
'''
if '/* DESKTOP_SLIDER_ZOOM_FIX */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

old_func = """      function ensureLightbox(){
        var box=document.querySelector('.image-lightbox');
        if(box){return box;}
        box=document.createElement('div');
        box.className='image-lightbox';
        box.innerHTML='<button type=\"button\" aria-label=\"닫기\">×</button><img alt=\"확대 이미지\">';
        document.body.appendChild(box);
        box.addEventListener('click',function(e){if(e.target===box || e.target.tagName==='BUTTON'){box.classList.remove('open');}});
        document.addEventListener('keydown',function(e){if(e.key==='Escape'){box.classList.remove('open');}});
        return box;
      }
      function openLightbox(src){
        var box=ensureLightbox();
        box.querySelector('img').src=src;
        box.classList.add('open');
      }"""
new_func = """      function ensureLightbox(){
        var box=document.querySelector('.slider-lightbox');
        if(box){return box;}
        box=document.createElement('div');
        box.className='slider-lightbox';
        box.innerHTML='<button type=\"button\" aria-label=\"닫기\">×</button><img alt=\"확대 이미지\">';
        document.body.appendChild(box);
        box.addEventListener('click',function(e){if(e.target===box || e.target.tagName==='BUTTON'){box.classList.remove('open');}});
        document.addEventListener('keydown',function(e){if(e.key==='Escape'){box.classList.remove('open');}});
        return box;
      }
      function openLightbox(src){
        var box=ensureLightbox();
        box.querySelector('img').src=src;
        box.classList.add('open');
      }"""
s = s.replace(old_func, new_func, 1)

# Open on pointerup too. PC sometimes does not fire click after pointer capture.
old_stop = """        function stop(){down=false;setTimeout(function(){moved=false;},80);slider.classList.remove('is-dragging');}
        slider.addEventListener('pointerup',stop);"""
new_stop = """        function stop(e){
          var img=e && e.target ? e.target.closest('img') : null;
          var wasMoved=moved;
          down=false;
          slider.classList.remove('is-dragging');
          if(img && !wasMoved){openLightbox(img.currentSrc||img.src);}
          setTimeout(function(){moved=false;},80);
        }
        slider.addEventListener('pointerup',stop);"""
s = s.replace(old_stop, new_stop, 1)

# Company intro mobile stays same flying action.
old_mobile_popup = """      if(window.innerWidth <= 760){
        section.classList.remove('prep');
        targetText.style.visibility='visible';
        targetText.classList.remove('mobile-burst');
        void targetText.offsetWidth;
        targetText.classList.add('mobile-burst');
        return;
      }

      section.classList.add('prep');
      targetText.style.visibility='hidden';"""
s = s.replace(old_mobile_popup, """      section.classList.add('prep');
      targetText.style.visibility='hidden';""", 1)
s = s.replace("const startTop=isMobile ? '39vh' : '50vh';", "const startTop=isMobile ? '45vh' : '50vh';")
s = s.replace("const startFont=isMobile ? '36px' : '80px';", "const startFont=isMobile ? '38px' : '80px';")
s = s.replace("const duration=isMobile ? 1250 : 950;", "const duration=isMobile ? 1500 : 950;")
s = s.replace("setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 160 : 40);", "setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);")

p.write_text(s, encoding='utf-8')
