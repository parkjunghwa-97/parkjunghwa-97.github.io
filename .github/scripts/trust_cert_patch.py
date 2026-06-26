from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep women-company document inside the certificate slider.
marquee = '''            <div class="cert-marquee" aria-hidden="true">
              <div class="cert-marquee-track">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/women-company.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/women-company.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/park-estate.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-clean.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-pest.jpg" alt="">
                <img decoding="async" loading="lazy" src="images/certificates/certificates/kim-estate.jpg" alt="">
              </div>
            </div>'''
start = s.find('            <div class="cert-marquee" aria-hidden="true">')
end_marker = '            <div class="cert-actions">'
if start != -1:
    end = s.find(end_marker, start)
    if end != -1:
        s = s[:start] + marquee + '\n' + s[end:]

css = '''

    /* DRAG_ZOOM_SLIDERS */
    .grab-slider{overflow-x:auto!important;overflow-y:hidden!important;cursor:grab!important;-webkit-overflow-scrolling:touch;scrollbar-width:none;touch-action:pan-x;user-select:none}
    .grab-slider::-webkit-scrollbar{display:none}
    .grab-slider.is-dragging{cursor:grabbing!important}
    .grab-slider .case-strip,.grab-slider .cert-marquee-track{animation:none!important}
    .grab-slider img{cursor:zoom-in;user-select:none;-webkit-user-drag:none}
    .image-lightbox{position:fixed;inset:0;background:rgba(15,23,42,.86);z-index:99999;display:none;align-items:center;justify-content:center;padding:18px}
    .image-lightbox.open{display:flex}
    .image-lightbox img{max-width:94vw;max-height:88vh;object-fit:contain;background:white;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.38)}
    .image-lightbox button{position:fixed;top:14px;right:14px;border:0;background:white;color:#0f172a;border-radius:999px;width:42px;height:42px;font-size:24px;font-weight:900;cursor:pointer}
'''
if '/* DRAG_ZOOM_SLIDERS */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

js = r'''

    /* DRAG_ZOOM_SLIDERS */
    (function(){
      function makeSlider(slider){
        if(!slider || slider.dataset.grabReady){return;}
        slider.dataset.grabReady='1';
        slider.classList.add('grab-slider');
        var track=slider.querySelector('.case-strip,.cert-marquee-track');
        if(track){track.style.animation='none';}
        var down=false,startX=0,startScroll=0,moved=false;
        slider.addEventListener('pointerdown',function(e){
          down=true;moved=false;startX=e.clientX;startScroll=slider.scrollLeft;slider.classList.add('is-dragging');
          try{slider.setPointerCapture(e.pointerId);}catch(err){}
        });
        slider.addEventListener('pointermove',function(e){
          if(!down){return;}
          var dx=e.clientX-startX;
          if(Math.abs(dx)>5){moved=true;}
          slider.scrollLeft=startScroll-dx;
        });
        function stop(){down=false;setTimeout(function(){moved=false;},80);slider.classList.remove('is-dragging');}
        slider.addEventListener('pointerup',stop);
        slider.addEventListener('pointercancel',stop);
        slider.addEventListener('mouseleave',function(){if(down){stop();}});
        slider.addEventListener('click',function(e){
          var img=e.target.closest('img');
          if(!img){return;}
          if(moved){e.preventDefault();return;}
          openLightbox(img.currentSrc||img.src);
        });
        var speed=slider.classList.contains('cert-marquee') ? 0.28 : 0.42;
        function auto(){
          if(!down && document.body.contains(slider)){
            slider.scrollLeft += speed;
            if(slider.scrollLeft >= (slider.scrollWidth - slider.clientWidth - 2)){slider.scrollLeft=0;}
          }
          requestAnimationFrame(auto);
        }
        requestAnimationFrame(auto);
      }
      function ensureLightbox(){
        var box=document.querySelector('.image-lightbox');
        if(box){return box;}
        box=document.createElement('div');
        box.className='image-lightbox';
        box.innerHTML='<button type="button" aria-label="닫기">×</button><img alt="확대 이미지">';
        document.body.appendChild(box);
        box.addEventListener('click',function(e){if(e.target===box || e.target.tagName==='BUTTON'){box.classList.remove('open');}});
        document.addEventListener('keydown',function(e){if(e.key==='Escape'){box.classList.remove('open');}});
        return box;
      }
      function openLightbox(src){
        var box=ensureLightbox();
        box.querySelector('img').src=src;
        box.classList.add('open');
      }
      function init(){
        document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);
      }
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
    })();
'''
if '/* DRAG_ZOOM_SLIDERS */' in s and js not in s:
    pos = s.rfind('</script>')
    if pos != -1:
        s = s[:pos] + js + s[pos:]

p.write_text(s, encoding='utf-8')
