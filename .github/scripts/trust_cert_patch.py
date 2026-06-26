from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Slider should keep moving; do not kill its action when making it draggable.
s = s.replace('.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important;width:max-content!important}',
              '.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{width:max-content!important}')
s = s.replace('.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{animation:none!important}',
              '.grab-slider .case-strip,.grab-slider .review-track,.grab-slider .cert-marquee-track{}')
s = s.replace("if(track){track.style.animation='none';}", "if(track){track.style.animationPlayState='running';}")

# Make review screenshots part of the draggable/zoomable sliders.
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")

# Re-initialize sliders whenever a menu page is opened, because hidden sections can have zero width on first load.
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

# Keep the same flying company intro action on mobile, not the card popup.
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
