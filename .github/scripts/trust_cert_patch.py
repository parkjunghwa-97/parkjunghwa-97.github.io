from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep slider moving while draggable.
s = s.replace("if(track){track.style.animation='none';}", "if(track){track.style.animationPlayState='running';}")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")

# Make company intro action slower and easier to see on mobile.
s = s.replace("const startTop=isMobile ? '45vh' : '50vh';", "const startTop=isMobile ? '38vh' : '50vh';")
s = s.replace("const startTop=isMobile ? '39vh' : '50vh';", "const startTop=isMobile ? '38vh' : '50vh';")
s = s.replace("const startFont=isMobile ? '38px' : '80px';", "const startFont=isMobile ? '36px' : '80px';")
s = s.replace("const startFont=isMobile ? '36px' : '80px';", "const startFont=isMobile ? '36px' : '80px';")
s = s.replace("const duration=isMobile ? 1500 : 950;", "const duration=isMobile ? 3200 : 950;")
s = s.replace("const duration=isMobile ? 1250 : 950;", "const duration=isMobile ? 3200 : 950;")
s = s.replace("{left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.26}", "{left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.18}")
s = s.replace("{left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(.92)',opacity:1,offset:.60}", "{left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(.98)',opacity:1,offset:.72}")
s = s.replace("setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 300 : 40);", "setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 450 : 40);")

# Keep the flying text visible above floating contact buttons.
css_about = '''

    /* MOBILE_ABOUT_ACTION_VISIBILITY */
    @media(max-width:760px){
      .fly-about-text{z-index:2147483646!important;color:#0f172a!important;text-shadow:0 10px 30px rgba(255,255,255,.98),0 2px 10px rgba(255,255,255,.96)!important}
    }
'''
if '/* MOBILE_ABOUT_ACTION_VISIBILITY */' not in s:
    s = s.replace('</style>', css_about + '\n</style>', 1)

# Strong lightbox CSS, independent from the older one.
css = '''

    /* UNIVERSAL_SLIDER_ZOOM */
    .universal-slider-lightbox{position:fixed!important;inset:0!important;background:rgba(15,23,42,.92)!important;z-index:2147483647!important;display:none;align-items:center;justify-content:center;padding:18px}
    .universal-slider-lightbox.open{display:flex!important}
    .universal-slider-lightbox img{max-width:94vw;max-height:88vh;object-fit:contain;background:#fff;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.42)}
    .universal-slider-lightbox button{position:fixed;top:14px;right:14px;border:0;background:#fff;color:#0f172a;border-radius:999px;width:42px;height:42px;font-size:24px;font-weight:900;cursor:pointer}
    .review-marquee img,.cert-marquee img,.case-row img{cursor:zoom-in!important}
'''
if '/* UNIVERSAL_SLIDER_ZOOM */' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

# Capture pointer events before the drag code can swallow the click.
js = r'''

    /* UNIVERSAL_SLIDER_ZOOM */
    (function(){
      var selector='.review-marquee img,.cert-marquee img,.case-row img';
      var down=null;
      var lastOpen=0;
      function getImg(e){
        return e && e.target && e.target.closest ? e.target.closest(selector) : null;
      }
      function box(){
        var el=document.querySelector('.universal-slider-lightbox');
        if(el){return el;}
        el=document.createElement('div');
        el.className='universal-slider-lightbox';
        el.innerHTML='<button type="button" aria-label="닫기">×</button><img alt="확대 이미지">';
        document.body.appendChild(el);
        el.addEventListener('click',function(e){if(e.target===el || e.target.tagName==='BUTTON'){el.classList.remove('open');}},true);
        document.addEventListener('keydown',function(e){if(e.key==='Escape'){el.classList.remove('open');}},true);
        return el;
      }
      function openImg(img){
        if(!img){return;}
        var now=Date.now();
        if(now-lastOpen<280){return;}
        lastOpen=now;
        var el=box();
        el.querySelector('img').src=img.currentSrc || img.src;
        el.classList.add('open');
      }
      document.addEventListener('pointerdown',function(e){
        var img=getImg(e);
        if(img){down={img:img,x:e.clientX,y:e.clientY};}
      },true);
      document.addEventListener('pointerup',function(e){
        if(!down){return;}
        var img=getImg(e) || down.img;
        var dx=Math.abs((e.clientX||0)-down.x);
        var dy=Math.abs((e.clientY||0)-down.y);
        var same=img===down.img;
        var smallMove=dx<9 && dy<9;
        down=null;
        if(same && smallMove){
          e.preventDefault();
          e.stopPropagation();
          openImg(img);
        }
      },true);
      document.addEventListener('click',function(e){
        var img=getImg(e);
        if(img){
          e.preventDefault();
          e.stopPropagation();
          openImg(img);
        }
      },true);
    })();
'''
if '/* UNIVERSAL_SLIDER_ZOOM */' not in s.split('</script>')[-2]:
    pos=s.rfind('</script>')
    if pos!=-1:
        s=s[:pos]+js+s[pos:]

p.write_text(s, encoding='utf-8')
