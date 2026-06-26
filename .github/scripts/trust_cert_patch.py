from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep the first JSON-LD block clean.
s = s.replace('''
    window.addEventListener('popstate', function(){
      const id=(location.hash||'#home').replace('#','');
      if(document.getElementById(id)){showPage(id,true);}
    });
    document.addEventListener('DOMContentLoaded', function(){
      const id=(location.hash||'').replace('#','');
      if(id && document.getElementById(id)){showPage(id,true);}
    });
''', '\n')

# Make the flying company-intro sentence visible on mobile.
fix_css = '''

    /* ABOUT_MOBILE_MOTION_FIX */
    @media(max-width:760px){.fly-about-text{z-index:99999!important;text-shadow:0 8px 28px rgba(255,255,255,.96),0 2px 10px rgba(255,255,255,.8)}}
'''
if '/* ABOUT_MOBILE_MOTION_FIX */' not in s:
    s = s.replace('</style>', fix_css + '\n</style>', 1)

old_show = '''      const target=document.getElementById(id);
      if(target){
        target.classList.add('active');
        if(id === 'about'){
          playAboutLanding(target);
        }
      }'''
new_show = '''      const target=document.getElementById(id);
      if(target){
        target.classList.add('active');
      }'''
s = s.replace(old_show, new_show, 1)

old_scroll = '''      if(!fromHistory && window.location.hash !== '#'+id){history.pushState({page:id},'', '#'+id);}
      window.scrollTo({top:0,behavior:'auto'});'''
new_scroll = '''      if(!fromHistory && window.location.hash !== '#'+id){history.pushState({page:id},'', '#'+id);}
      window.scrollTo({top:0,behavior:'auto'});

      if(target && id === 'about'){
        setTimeout(function(){playAboutLanding(target);}, window.innerWidth <= 760 ? 160 : 40);
      }'''
s = s.replace(old_scroll, new_scroll, 1)

old_anim = '''        const startWidth=Math.min(window.innerWidth * 0.92, 980);
        fly.style.left='50vw';
        fly.style.top='50vh';
        fly.style.width=startWidth + 'px';
        fly.style.fontSize=window.innerWidth <= 760 ? '34px' : '80px';
        fly.style.transform='translate(-50%,-50%) scale(1)';
        fly.style.opacity='0';

        const animation=fly.animate([
          {left:'50vw',top:'50vh',width:startWidth+'px',fontSize:window.innerWidth<=760?'34px':'80px',transform:'translate(-50%,-50%) scale(1.18)',opacity:0,offset:0},
          {left:'50vw',top:'50vh',width:startWidth+'px',fontSize:window.innerWidth<=760?'34px':'80px',transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.24},
          {left:'50vw',top:'50vh',width:startWidth+'px',fontSize:window.innerWidth<=760?'34px':'80px',transform:'translate(-50%,-50%) scale(.92)',opacity:1,offset:.55},
          {left:rect.left+'px',top:rect.top+'px',width:rect.width+'px',fontSize:style.fontSize,transform:'translate(0,0) scale(1)',opacity:1,offset:1}
        ],{duration:950,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});'''
new_anim = '''        const isMobile=window.innerWidth <= 760;
        const startWidth=Math.min(window.innerWidth * (isMobile ? 0.86 : 0.92), 980);
        const startTop=isMobile ? '39vh' : '50vh';
        const startFont=isMobile ? '36px' : '80px';
        const duration=isMobile ? 1250 : 950;
        fly.style.left='50vw';
        fly.style.top=startTop;
        fly.style.width=startWidth + 'px';
        fly.style.fontSize=startFont;
        fly.style.transform='translate(-50%,-50%) scale(1)';
        fly.style.opacity='0';

        const animation=fly.animate([
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1.16)',opacity:0,offset:0},
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.26},
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(.92)',opacity:1,offset:.60},
          {left:rect.left+'px',top:rect.top+'px',width:rect.width+'px',fontSize:style.fontSize,transform:'translate(0,0) scale(1)',opacity:1,offset:1}
        ],{duration:duration,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});'''
s = s.replace(old_anim, new_anim, 1)

p.write_text(s, encoding='utf-8')
