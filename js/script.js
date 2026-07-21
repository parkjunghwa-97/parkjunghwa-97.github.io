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

    /* CASES_JSON_INTEGRATION */
    (function(){
      var CASE_LIMIT=12;
      var CASE_ENDPOINT='/data/cases.json';

      function onReady(fn){
        if(document.readyState==='loading'){
          document.addEventListener('DOMContentLoaded',fn);
        }else{
          fn();
        }
      }

      function cleanText(value){
        return typeof value === 'string' ? value.trim() : '';
      }

      function cleanBool(value){
        return value === true || value === 'true';
      }

      function normalizeCase(item){
        return {
          id: cleanText(item && item.id),
          service: cleanText(item && item.service),
          region: cleanText(item && item.region),
          title: cleanText(item && item.title),
          description: cleanText(item && item.description),
          image: cleanText(item && item.image),
          date: cleanText(item && item.date),
          featured: cleanBool(item && item.featured)
        };
      }

      function isUsableCase(item){
        return item.service && item.region && item.title && item.description;
      }

      function imageSrc(src){
        var value=cleanText(src);
        if(!value){return '';}
        if(value.indexOf('data:') === 0 || /^https?:\/\//i.test(value) || value.indexOf('/') === 0 || value.indexOf('../') === 0){
          return value;
        }
        return '/' + value.replace(/^\.\/+/, '');
      }

      function appendCasePhoto(parent,src,title){
        var srcValue=imageSrc(src);
        if(!srcValue){return;}

        var wrap=document.createElement('div');
        wrap.className='case-json-image';

        var img=document.createElement('img');
        img.src=srcValue;
        img.alt=(title ? title + ' ' : '') + '\uC791\uC5C5 \uC0AC\uC9C4';
        img.loading='lazy';
        img.decoding='async';
        wrap.appendChild(img);

        parent.appendChild(wrap);
      }

      function createCaseCard(item){
        var article=document.createElement('article');
        article.className='case-mini case-json-card';
        article.setAttribute('data-case-id',item.id || '');

        appendCasePhoto(article,item.image,item.title);

        var service=document.createElement('span');
        service.className='case-json-service';
        service.textContent=item.service;
        article.appendChild(service);

        var region=document.createElement('span');
        region.className='case-json-region';
        region.textContent=item.region;
        article.appendChild(region);

        var title=document.createElement('b');
        title.textContent=item.title;
        article.appendChild(title);

        var description=document.createElement('p');
        description.textContent=item.description;
        article.appendChild(description);

        return article;
      }

      function renderCases(target,items){
        var fragment=document.createDocumentFragment();
        items.slice(0,CASE_LIMIT).forEach(function(item){
          fragment.appendChild(createCaseCard(item));
        });
        if(!fragment.childNodes.length){return;}
        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-cases-source','json');
      }

      function initCasesJson(){
        var target=document.querySelector('[data-cases-json-target="true"]');
        if(!target || !window.fetch){return;}

        window.fetch(CASE_ENDPOINT,{cache:'no-store'})
          .then(function(response){
            if(!response.ok){throw new Error('cases json failed');}
            return response.json();
          })
          .then(function(data){
            var cases=Array.isArray(data) ? data.map(normalizeCase).filter(isUsableCase) : [];
            if(cases.length){
              renderCases(target,cases);
            }
          })
          .catch(function(){
            target.setAttribute('data-cases-source','fallback');
          });
      }

      onReady(initCasesJson);
    })();


    /* PRICES_JSON_INTEGRATION */
    (function(){
      var PRICE_LIMIT=30;
      var PRICE_ENDPOINT='/data/prices.json';

      function onReady(fn){
        if(document.readyState==='loading'){
          document.addEventListener('DOMContentLoaded',fn);
        }else{
          fn();
        }
      }

      function cleanText(value){
        return typeof value === 'string' ? value.trim() : '';
      }

      function cleanVisible(value){
        return value !== false && value !== 'false';
      }

      function cleanSort(value){
        var sort=Number(value || 0);
        return isFinite(sort) ? sort : 0;
      }

      function normalizePrice(item){
        return {
          id: cleanText(item && item.id),
          category: cleanText(item && item.category),
          title: cleanText(item && item.title),
          price: cleanText(item && item.price),
          description: cleanText(item && item.description),
          visible: cleanVisible(item && item.visible),
          sort: cleanSort(item && item.sort)
        };
      }

      function isUsablePrice(item){
        return item.visible && item.category && item.title && item.price;
      }

      function createPriceRow(item){
        var row=document.createElement('div');
        row.className='price-row price-json-row';
        row.setAttribute('data-price-id',item.id || '');

        var copy=document.createElement('div');
        copy.className='price-json-copy';

        var title=document.createElement('span');
        title.className='price-json-title';
        title.textContent=item.title;
        copy.appendChild(title);

        if(item.description){
          var description=document.createElement('small');
          description.textContent=item.description;
          copy.appendChild(description);
        }

        var price=document.createElement('span');
        price.className='price-json-amount';
        price.textContent=item.price;

        row.appendChild(copy);
        row.appendChild(price);
        return row;
      }

      function createPriceCard(group){
        var card=document.createElement('div');
        card.className='price-card price-json-card';

        var title=document.createElement('h3');
        title.textContent=group.category;
        card.appendChild(title);

        group.items.forEach(function(item){
          card.appendChild(createPriceRow(item));
        });

        return card;
      }

      function groupPrices(items){
        var groups=[];
        var byCategory={};
        items.forEach(function(item){
          if(!byCategory[item.category]){
            byCategory[item.category]={category:item.category,items:[]};
            groups.push(byCategory[item.category]);
          }
          byCategory[item.category].items.push(item);
        });
        return groups;
      }

      function renderPrices(target,items){
        var prices=items.slice().sort(function(a,b){return a.sort-b.sort;}).slice(0,PRICE_LIMIT);
        var groups=groupPrices(prices);
        var fragment=document.createDocumentFragment();
        groups.forEach(function(group){
          fragment.appendChild(createPriceCard(group));
        });
        if(!fragment.childNodes.length){return;}
        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-prices-source','json');
      }

      function initPricesJson(){
        var target=document.querySelector('[data-prices-json-target=true]');
        if(!target || !window.fetch){return;}

        window.fetch(PRICE_ENDPOINT,{cache:'no-store'})
          .then(function(response){
            if(!response.ok){throw new Error('prices json failed');}
            return response.json();
          })
          .then(function(data){
            var prices=Array.isArray(data) ? data.map(normalizePrice).filter(isUsablePrice) : [];
            if(prices.length){
              renderPrices(target,prices);
            }
          })
          .catch(function(){
            target.setAttribute('data-prices-source','fallback');
          });
      }

      onReady(initPricesJson);
    })();


    /* CONTENT_JSON_INTEGRATION */
    (function(){
      var FAQ_LIMIT=100;
      var NOTICE_LIMIT=50;
      var BANNER_LIMIT=20;
      var FAQ_ENDPOINT='/data/faq.json';
      var NOTICE_ENDPOINT='/data/notices.json';
      var BANNER_ENDPOINT='/data/banners.json';

      function onReady(fn){
        if(document.readyState==='loading'){
          document.addEventListener('DOMContentLoaded',fn);
        }else{
          fn();
        }
      }

      function cleanText(value){
        return typeof value === 'string' ? value.trim() : '';
      }

      function cleanVisible(value){
        return value !== false && value !== 'false';
      }

      function cleanSort(value){
        var sort=Number(value || 0);
        return isFinite(sort) ? sort : 0;
      }

      function bySort(a,b){
        return a.sort-b.sort;
      }

      function fetchJson(endpoint,onSuccess,onFail){
        window.fetch(endpoint,{cache:'no-store'})
          .then(function(response){
            if(!response.ok){throw new Error('content json failed');}
            return response.json();
          })
          .then(onSuccess)
          .catch(onFail);
      }

      function normalizeFaq(item){
        return {
          id: cleanText(item && item.id),
          question: cleanText(item && item.question),
          answer: cleanText(item && item.answer),
          visible: cleanVisible(item && item.visible),
          sort: cleanSort(item && item.sort)
        };
      }

      function isUsableFaq(item){
        return item.visible && item.question && item.answer;
      }

      function createFaqCard(item){
        var card=document.createElement('div');
        card.className='faq-card';
        card.setAttribute('data-faq-id',item.id || '');

        var question=document.createElement('b');
        question.textContent=item.question;
        card.appendChild(question);

        var answer=document.createElement('p');
        answer.textContent=item.answer;
        card.appendChild(answer);

        return card;
      }

      function renderFaq(target,items){
        var faqs=items.slice().sort(bySort).slice(0,FAQ_LIMIT);
        var fragment=document.createDocumentFragment();
        faqs.forEach(function(item){
          fragment.appendChild(createFaqCard(item));
        });
        if(!fragment.childNodes.length){return;}
        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-faq-source','json');
      }

      function initFaqJson(){
        var target=document.querySelector('[data-faq-json-target="true"]');
        if(!target || !window.fetch){return;}

        fetchJson(FAQ_ENDPOINT,function(data){
          var faqs=Array.isArray(data) ? data.map(normalizeFaq).filter(isUsableFaq) : [];
          if(faqs.length){
            renderFaq(target,faqs);
          }
        },function(){
          target.setAttribute('data-faq-source','fallback');
        });
      }

      function normalizeNotice(item){
        return {
          id: cleanText(item && item.id),
          title: cleanText(item && item.title),
          content: cleanText(item && item.content),
          date: cleanText(item && item.date),
          visible: cleanVisible(item && item.visible),
          sort: cleanSort(item && item.sort)
        };
      }

      function isUsableNotice(item){
        return item.visible && item.title && item.content;
      }

      function createNoticeCard(item){
        var article=document.createElement('article');
        article.className='notice-card';
        article.setAttribute('data-notice-id',item.id || '');

        var title=document.createElement('h3');
        title.textContent=item.title;
        article.appendChild(title);

        var content=document.createElement('p');
        content.textContent=item.content;
        article.appendChild(content);

        if(item.date){
          var date=document.createElement('small');
          date.textContent=item.date;
          article.appendChild(date);
        }

        return article;
      }

      function renderNotices(target,items){
        var notices=items.slice().sort(bySort).slice(0,NOTICE_LIMIT);
        var fragment=document.createDocumentFragment();
        notices.forEach(function(item){
          fragment.appendChild(createNoticeCard(item));
        });
        if(!fragment.childNodes.length){return;}
        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-notices-source','json');
      }

      function initNoticesJson(){
        var target=document.querySelector('[data-notices-json-target="true"]');
        if(!target || !window.fetch){return;}

        fetchJson(NOTICE_ENDPOINT,function(data){
          var notices=Array.isArray(data) ? data.map(normalizeNotice).filter(isUsableNotice) : [];
          if(notices.length){
            renderNotices(target,notices);
          }
        },function(){
          target.setAttribute('data-notices-source','fallback');
        });
      }

      function normalizeBanner(item){
        return {
          id: cleanText(item && item.id),
          title: cleanText(item && item.title),
          description: cleanText(item && item.description),
          button: cleanText(item && item.button),
          link: cleanText(item && item.link),
          visible: cleanVisible(item && item.visible),
          sort: cleanSort(item && item.sort)
        };
      }

      function isUsableBanner(item){
        return item.visible && item.title && item.description;
      }

      function createBannerButton(item,index){
        if(!item.button){return null;}

        var button=document.createElement('a');
        button.className='hero-btn' + (index ? ' secondary' : '');
        button.href=item.link || '#contact';
        button.textContent=item.button;
        button.addEventListener('click',function(event){
          var link=item.link || '';
          if(link.charAt(0) !== '#'){return;}
          var pageId=link.slice(1);
          if(!pageId || !document.getElementById(pageId) || typeof showPage !== 'function'){return;}
          event.preventDefault();
          showPage(pageId);
        });
        return button;
      }

      function createBannerCard(item,index){
        var article=document.createElement('article');
        article.className=index ? 'hero-json-banner' : 'hero-json-banner hero-json-banner-primary';
        article.setAttribute('data-banner-id',item.id || '');

        var title=document.createElement(index ? 'h2' : 'h1');
        title.className=index ? 'hero-banner-title' : 'hero-main';
        title.textContent=item.title;
        article.appendChild(title);

        var description=document.createElement('div');
        description.className=index ? 'hero-banner-description' : 'hero-sub';
        description.textContent=item.description;
        article.appendChild(description);

        var button=createBannerButton(item,index);
        if(button){
          var cta=document.createElement('div');
          cta.className='hero-cta';
          cta.appendChild(button);
          article.appendChild(cta);
        }

        return article;
      }

      function renderBanners(target,items){
        var banners=items.slice().sort(bySort).slice(0,BANNER_LIMIT);
        var fragment=document.createDocumentFragment();
        banners.forEach(function(item,index){
          fragment.appendChild(createBannerCard(item,index));
        });
        if(!fragment.childNodes.length){return;}
        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-banners-source','json');
      }

      function initBannersJson(){
        var target=document.querySelector('[data-banners-json-target="true"]');
        if(!target || !window.fetch){return;}

        fetchJson(BANNER_ENDPOINT,function(data){
          var banners=Array.isArray(data) ? data.map(normalizeBanner).filter(isUsableBanner) : [];
          if(banners.length){
            renderBanners(target,banners);
          }
        },function(){
          target.setAttribute('data-banners-source','fallback');
        });
      }

      onReady(initFaqJson);
      onReady(initNoticesJson);
      onReady(initBannersJson);
    })();

    /* SERVICES_JSON_INTEGRATION */
    // PR-C1a: 구조만 추가(data/services.json은 빈 배열). 실제 12개 서비스 본문은
    // PR-C1b에서 작성 예정이며, 확정된 목록과 sort 순서는 다음과 같습니다.
    //   1 특수청소, 2 쓰레기집청소, 3 고독사 특수청소, 4 유품정리, 5 화재청소,
    //   6 침수청소, 7 비둘기 퇴치, 8 폐기물 처리, 9 입주청소, 10 이사청소,
    //   11 거주청소, 12 상가·식당·사무실 청소
    // 메인 브랜드 정체성은 "특수청소 중심 종합 청소업체"이며, 이 순서는 그
    // 우선순위를 반영합니다(상가·식당·사무실 청소가 메인을 대체하지 않음).
    (function(){
      var SERVICES_LIMIT=30;
      var SERVICES_ENDPOINT='/data/services.json';

      function onReady(fn){
        if(document.readyState==='loading'){
          document.addEventListener('DOMContentLoaded',fn);
        }else{
          fn();
        }
      }

      function cleanText(value){
        return typeof value === 'string' ? value.trim() : '';
      }

      function cleanVisible(value){
        return value !== false && value !== 'false';
      }

      function cleanSort(value){
        var sort=Number(value || 0);
        return isFinite(sort) ? sort : 0;
      }

      function bySort(a,b){
        return a.sort-b.sort;
      }

      function normalizeService(item){
        return {
          id: cleanText(item && item.id),
          service: cleanText(item && item.service),
          seoTitle: cleanText(item && item.seoTitle),
          summary: cleanText(item && item.summary),
          description: cleanText(item && item.description),
          scope: cleanText(item && item.scope),
          process: cleanText(item && item.process),
          priceNote: cleanText(item && item.priceNote),
          notes: cleanText(item && item.notes),
          ctaText: cleanText(item && item.ctaText),
          visible: cleanVisible(item && item.visible),
          sort: cleanSort(item && item.sort)
        };
      }

      function isUsableService(item){
        return item.visible && item.service && item.summary && item.description;
      }

      function appendServiceField(container,label,value){
        if(!value){return;}
        var row=document.createElement('p');
        var strong=document.createElement('strong');
        strong.textContent=label + ': ';
        row.appendChild(strong);
        row.appendChild(document.createTextNode(value));
        container.appendChild(row);
      }

      function createServiceDetail(item){
        var details=document.createElement('details');
        details.setAttribute('data-service-id',item.id || '');

        var summary=document.createElement('summary');
        summary.textContent=item.service;
        details.appendChild(summary);

        var body=document.createElement('div');
        body.className='policy-content';

        var description=document.createElement('p');
        description.textContent=item.description;
        body.appendChild(description);

        appendServiceField(body,'작업 범위',item.scope);
        appendServiceField(body,'진행 순서',item.process);
        appendServiceField(body,'가격 기준',item.priceNote);
        appendServiceField(body,'주의사항',item.notes);

        if(item.ctaText){
          var cta=document.createElement('p');
          cta.className='service-detail-cta';
          cta.textContent=item.ctaText;
          body.appendChild(cta);
        }

        details.appendChild(body);
        return details;
      }

      function appendPositioningLead(fragment){
        var lead=document.createElement('p');
        lead.className='service-positioning-lead';
        lead.appendChild(document.createTextNode('기프트클린은 특수청소를 중심으로 쓰레기집청소·고독사 특수청소·유품정리·화재·침수청소·비둘기 퇴치·폐기물 처리부터 입주·이사·거주청소, 상가·식당·사무실 청소까지 전국 출장 서비스를 진행합니다.'));
        lead.appendChild(document.createElement('br'));
        lead.appendChild(document.createTextNode('별도 출장비 없이 현장 상태를 기준으로 안내드립니다.'));
        fragment.appendChild(lead);
      }

      function renderServices(target,items){
        var services=items.slice().sort(bySort).slice(0,SERVICES_LIMIT);
        if(!services.length){return;}

        var fragment=document.createDocumentFragment();

        var heading=document.createElement('h3');
        heading.textContent='서비스별 상세 안내';
        fragment.appendChild(heading);

        // services.json이 비어있을 때는(위의 이른 return) 이 문구도 함께 노출되지
        // 않습니다. 데이터가 1개 이상 있을 때만 상세 목록과 함께 보여줍니다.
        appendPositioningLead(fragment);

        services.forEach(function(item){
          fragment.appendChild(createServiceDetail(item));
        });

        target.innerHTML='';
        target.appendChild(fragment);
        target.setAttribute('data-services-source','json');
      }

      function initServicesJson(){
        var target=document.querySelector('[data-services-json-target="true"]');
        if(!target || !window.fetch){return;}

        window.fetch(SERVICES_ENDPOINT,{cache:'no-store'})
          .then(function(response){
            if(!response.ok){throw new Error('services json failed');}
            return response.json();
          })
          .then(function(data){
            var services=Array.isArray(data) ? data.map(normalizeService).filter(isUsableService) : [];
            if(services.length){
              renderServices(target,services);
            }
          })
          .catch(function(){
            target.setAttribute('data-services-source','fallback');
          });
      }

      onReady(initServicesJson);
    })();

    /* SLIDER_IMAGE_PRELOAD */
    (function(){
      window.preloadSliderImages=function(scope){
        var root=scope || document;
        var imgs=root.querySelectorAll('.review-marquee img,.cert-marquee img,.case-row img');
        imgs.forEach(function(img,idx){
          try{
            if(img.closest('.case-json-card')){return;}
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

/* REVIEW_JSON_INTEGRATION */
(function(){
  var REVIEW_LIMIT=12;
  var REVIEW_ENDPOINT='/data/reviews.json';

  function onReady(fn){
    if(document.readyState==='loading'){
      document.addEventListener('DOMContentLoaded',fn);
    }else{
      fn();
    }
  }

  function cleanText(value){
    return typeof value === 'string' ? value.trim() : '';
  }

  function cleanRating(value){
    var rating=Number(value || 5);
    if(!isFinite(rating)){rating=5;}
    return Math.max(1,Math.min(5,Math.round(rating)));
  }

  function normalizeReview(item){
    return {
      service: cleanText(item && item.service),
      region: cleanText(item && item.region),
      title: cleanText(item && item.title),
      rating: cleanRating(item && item.rating),
      content: cleanText(item && item.content),
      image: cleanText(item && item.image),
      source: cleanText(item && item.source),
      date: cleanText(item && item.date)
    };
  }

  function isUsableReview(review){
    return review.title && review.content && review.service && review.region;
  }

  function imageSrc(src){
    var value=cleanText(src);
    if(!value){return '';}
    if(value.indexOf('data:')===0 || /^https?:\/\//i.test(value) || value.indexOf('/')===0 || value.indexOf('../')===0){
      return value;
    }
    return '/' + value.replace(/^\.\/+/, '');
  }

  function appendReviewImage(parent,src,title){
    var srcValue=imageSrc(src);
    if(!srcValue){return;}

    var img=document.createElement('img');
    img.className='review-json-image';
    img.src=srcValue;
    img.alt=(title ? title + ' ' : '') + 'review image';
    img.loading='lazy';
    img.decoding='async';
    img.style.display='block';
    img.style.width='100%';
    img.style.height='150px';
    img.style.objectFit='cover';
    img.style.borderRadius='16px';
    img.style.margin='0 0 14px';
    img.style.background='#f1f5f9';
    parent.appendChild(img);
  }

  function createReviewCard(review){
    var article=document.createElement('article');
    article.className='review-text-card';
    article.setAttribute('data-review-source','json');

    appendReviewImage(article,review.image,review.title);

    var title=document.createElement('b');
    title.textContent=review.title;
    article.appendChild(title);

    var meta=document.createElement('span');
    meta.textContent=review.service + ' · ' + review.region + ' · ★ ' + review.rating;
    article.appendChild(meta);

    var content=document.createElement('p');
    content.textContent='“' + review.content + '”';
    article.appendChild(content);

    if(review.source || review.date){
      var source=document.createElement('small');
      source.textContent=[review.source,review.date].filter(Boolean).join(' · ');
      article.appendChild(source);
    }

    return article;
  }

  function renderReviews(target,reviews){
    var fragment=document.createDocumentFragment();
    reviews.slice(0,REVIEW_LIMIT).forEach(function(review){
      fragment.appendChild(createReviewCard(review));
    });
    if(!fragment.childNodes.length){return;}
    target.innerHTML='';
    target.appendChild(fragment);
    target.setAttribute('data-reviews-source','json');
  }

  function initReviewsJson(){
    var target=document.querySelector('[data-reviews-json-target="true"]');
    if(!target || !window.fetch){return;}

    window.fetch(REVIEW_ENDPOINT,{cache:'no-store'})
      .then(function(response){
        if(!response.ok){throw new Error('reviews json failed');}
        return response.json();
      })
      .then(function(data){
        var reviews=Array.isArray(data) ? data.map(normalizeReview).filter(isUsableReview) : [];
        if(reviews.length){
          renderReviews(target,reviews);
        }
      })
      .catch(function(){
        target.setAttribute('data-reviews-source','fallback');
      });
  }

  onReady(initReviewsJson);
})();
