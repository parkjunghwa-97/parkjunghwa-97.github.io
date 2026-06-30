    function showPage(id, fromHistory){
      document.querySelectorAll('.fly-about-text').forEach(function(el){
        if(el.parentNode){
          el.parentNode.removeChild(el);
        }
      });
      document.querySelectorAll('.page').forEach(function(page){
        page.classList.remove('active');
        page.classList.remove('prep');
      });

      const target=document.getElementById(id);
      if(target){
        target.classList.add('active');
      }

      document.querySelectorAll('.nav-btn').forEach(function(btn){
        btn.classList.remove('active');
      });

      document.querySelectorAll('.nav-btn').forEach(function(btn){
        const clickValue=btn.getAttribute('onclick')||'';
        if(clickValue.includes("'" + id + "'")){
          btn.classList.add('active');
        }
      });

      if(!fromHistory && window.location.hash !== '#'+id){history.pushState({page:id},'', '#'+id);}
      window.scrollTo({top:0,behavior:'auto'});

      if(target && id === 'about'){
        scheduleAboutLanding(target);
      }
      if(window.initSliders){setTimeout(window.initSliders, 80);}
      if(window.preloadSliderImages){setTimeout(function(){window.preloadSliderImages(target || document);}, 90);}
      if(window.preloadSliderImages){setTimeout(function(){window.preloadSliderImages(target || document);}, 90);}
      if(window.initSliders){setTimeout(window.initSliders, 80);}
      if(window.initSliders){setTimeout(window.initSliders, 80);}
    }

    function scheduleAboutLanding(target){
      if(target && target.classList.contains('active')){
        playAboutLanding(target);
      }
    }

    function playAboutLanding(section){
      if(!section || section.dataset.aboutAnimating === '1'){return}

      const content=section.querySelector('.about-content');
      const targetText=section.querySelector('.about-highlight');
      if(!content || !targetText){return}

      section.dataset.aboutAnimating='1';
      section.classList.add('prep');
      targetText.style.visibility='hidden';

      const runLanding=function(){
        const rect=targetText.getBoundingClientRect();
        const style=getComputedStyle(targetText);

        const fly=document.createElement('div');
        fly.className='fly-about-text';
        fly.textContent='새로운 시작이 필요하기 때문입니다.';
        document.body.appendChild(fly);

        const isMobile=window.innerWidth <= 760;
        const startWidth=Math.min(window.innerWidth * (isMobile ? 0.86 : 0.92), 980);
        const startTop=isMobile ? '43vh' : '50vh';
        const startFont=isMobile ? '37px' : '80px';
        const duration=isMobile ? 1750 : 950;
        fly.style.left='50vw';
        fly.style.top=startTop;
        fly.style.width=startWidth + 'px';
        fly.style.fontSize=startFont;
        fly.style.transform='translate(-50%,-50%) scale(1)';
        fly.style.opacity='0';

        let finished=false;
        const finish=function(){
          if(finished){return}
          finished=true;
          if(fly.parentNode){
            fly.parentNode.removeChild(fly);
          }
          targetText.style.visibility='visible';
          section.classList.remove('prep');
          delete section.dataset.aboutAnimating;
        };
        setTimeout(finish, duration + 250);

        const keyframes=[
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1.16)',opacity:0,offset:0},
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(1)',opacity:1,offset:.24},
          {left:'50vw',top:startTop,width:startWidth+'px',fontSize:startFont,transform:'translate(-50%,-50%) scale(.94)',opacity:1,offset:.58},
          {left:rect.left+'px',top:rect.top+'px',width:rect.width+'px',fontSize:style.fontSize,transform:'translate(0,0) scale(1)',opacity:1,offset:1}
        ];

        if(typeof fly.animate === 'function'){
          const animation=fly.animate(keyframes,{duration:duration,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'});
          animation.onfinish=finish;
          if(animation.finished && typeof animation.finished.then === 'function'){
            animation.finished.then(finish).catch(function(){});
          }
        }else{
          fly.style.opacity='1';
          setTimeout(finish, duration);
        }
      };

      if(typeof requestAnimationFrame === 'function'){
        requestAnimationFrame(runLanding);
      }else{
        setTimeout(runLanding, 0);
      }
    }

    document.addEventListener('DOMContentLoaded', function(){
      setTimeout(function(){
        const home = document.getElementById('home');
        if(home){
          home.classList.add('active');
        }
      }, 3200);

      document.addEventListener('click', function(event){
        const trigger=event.target.closest('[onclick]');
        const clickValue=trigger ? (trigger.getAttribute('onclick') || '') : '';
        if(clickValue.indexOf("showPage('about')") === -1 && clickValue.indexOf('showPage("about")') === -1){return}

        setTimeout(function(){
          const about=document.getElementById('about');
          if(about){
            scheduleAboutLanding(about);
          }
        }, 0);
      }, true);

      const about=document.getElementById('about');
      if(about && typeof MutationObserver === 'function'){
        let aboutWasActive=about.classList.contains('active');
        const aboutObserver=new MutationObserver(function(){
          const aboutIsActive=about.classList.contains('active');
          if(aboutIsActive && !aboutWasActive){
            scheduleAboutLanding(about);
          }
          aboutWasActive=aboutIsActive;
        });
        aboutObserver.observe(about,{attributes:true,attributeFilter:['class']});
      }
    });

    function handleContactSubmit(event){
      const form = event.target;
      const submitBtn = form.querySelector('.submit-btn');
      const successBox = document.getElementById('formSuccess');

      submitBtn.disabled = true;
      submitBtn.textContent = '접수 중...';

      setTimeout(function(){
        successBox.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = '📝 상담 예약하기';
        form.reset();
      }, 1200);
    }


    /* DRAG_ZOOM_SLIDERS */
    (function(){
      function makeSlider(slider){
        if(!slider || slider.dataset.grabReady){return;}
        slider.dataset.grabReady='1';
        slider.classList.add('grab-slider');
        var track=slider.querySelector('.case-strip,.review-track,.cert-marquee-track');
        if(track){track.style.animationPlayState='running';}
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
        function stop(e){
          var img=e && e.target ? e.target.closest('img') : null;
          var wasMoved=moved;
          down=false;
          slider.classList.remove('is-dragging');
          if(img && !wasMoved){openLightbox(img.currentSrc||img.src);}
          setTimeout(function(){moved=false;},80);
        }
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
        var box=document.querySelector('.slider-lightbox');
        if(box){return box;}
        box=document.createElement('div');
        box.className='slider-lightbox';
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
      window.initSliders=function(){
        document.querySelectorAll('.case-row,.review-marquee,.cert-marquee').forEach(makeSlider);
      };
      function init(){window.initSliders();}
      if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
    })();


    /* SLIDER_IMAGE_PRELOAD */
    (function(){
      window.preloadSliderImages=function(scope){
        var root=scope || document;
        var imgs=root.querySelectorAll('.review-marquee img,.cert-marquee img,.case-row img');
        imgs.forEach(function(img,idx){
          try{
            img.loading='eager';
            img.decoding='async';
            if(idx<4){img.fetchPriority='high';}
            var pre=new Image();
            pre.decoding='async';
            pre.src=img.currentSrc || img.src;
          }catch(e){}
        });
      };
      if(document.readyState==='loading'){
        document.addEventListener('DOMContentLoaded',function(){setTimeout(function(){window.preloadSliderImages(document);},900);});
      }else{
        setTimeout(function(){window.preloadSliderImages(document);},900);
      }
    })();


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

/* REVIEW_TEXT_DRAG */
(function(){
  function initReviewTextDrag(){
    document.querySelectorAll('.review-text-scroll').forEach(function(el){
      if(el.dataset.dragReady){return;}
      el.dataset.dragReady='1';
      var down=false,startX=0,startScroll=0;
      el.addEventListener('pointerdown',function(e){
        down=true;startX=e.clientX;startScroll=el.scrollLeft;el.classList.add('is-dragging');
        try{el.setPointerCapture(e.pointerId);}catch(err){}
      });
      el.addEventListener('pointermove',function(e){
        if(!down){return;}
        el.scrollLeft=startScroll-(e.clientX-startX);
      });
      function stop(){down=false;el.classList.remove('is-dragging');}
      el.addEventListener('pointerup',stop);
      el.addEventListener('pointercancel',stop);
      el.addEventListener('mouseleave',function(){if(down){stop();}});
    });
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',initReviewTextDrag);}else{initReviewTextDrag();}
})();
