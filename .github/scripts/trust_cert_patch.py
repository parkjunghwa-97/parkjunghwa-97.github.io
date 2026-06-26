from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep slider moving while draggable.
s = s.replace("if(track){track.style.animation='none';}", "if(track){track.style.animationPlayState='running';}")
s = s.replace("document.querySelectorAll('.case-row,.cert-marquee').forEach(makeSlider);", "document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);")
s = s.replace("var track=slider.querySelector('.case-strip,.cert-marquee-track');", "var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');")

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
