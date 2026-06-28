from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('\ud604\uc7a5\uc77c\uc9c0','\ud604\uc7a5\uae30\ub85d')
s=s.replace('\uc791\uc5c5\uc0ac\ub840 \ud15c\ud50c\ub9bf \ubcf4\uae30','\ud604\uc7a5\uae30\ub85d \ubcf4\uae30')
s=s.replace('<p class="sub">\uc2e4\uc81c \ud604\uc7a5\ubcc4 \uc791\uc5c5 \ub0b4\uc6a9\uacfc \uc815\ubcf4\uc131 \ucf58\ud150\uce20\ub97c \uc9c0\uc5ed, \uc11c\ube44\uc2a4, \uc791\uc5c5 \ubc94\uc704 \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud558\ub294 \uacf5\uac04\uc785\ub2c8\ub2e4.</p>','')
s=s.replace('<a href="/cases/">\uccb4\ud06c\ub9ac\uc2a4\ud2b8 \ubcf4\uae30</a>','<p>\uc785\uc8fc \uc804 \ud655\uc778 \uae30\uc900\uc744 \ud56d\ubaa9\ubcc4\ub85c \uc815\ub9ac\ud558\ub294 \uc815\ubcf4\ud615 \uae00\uc785\ub2c8\ub2e4.</p>')
s=s.replace('<a href="/cases/">\uc0ac\uc9c4\uc0c1\ub2f4 \uae30\uc900 \ubcf4\uae30</a>','<p>\uc0ac\uc9c4\uc0c1\ub2f4 \uc804\uc5d0 \ud544\uc694\ud55c \uc0ac\uc9c4 \uae30\uc900\uc744 \uc815\ub9ac\ud558\ub294 \uae00\uc785\ub2c8\ub2e4.</p>')
s=s.replace('<a href="/cases/">\ud604\uc7a5\uae30\ub85d \ubcf4\uae30</a>','<p>\uc2e4\uc81c \ud604\uc7a5 \uae30\uc900\uc73c\ub85c \uc791\uc5c5 \ubc94\uc704\ub97c \uc815\ub9ac\ud558\ub294 \uae00\uc785\ub2c8\ub2e4.</p>')
extra='''<article class="journal-card"><span>\ube44\ub458\uae30 \ud1f4\uce58</span><h3>\ube44\ub458\uae30 \ud1f4\uce58 \uc804 \ud655\uc778\ud560 \uc0ac\ud56d</h3><p>\ubd84\ubcc0 \uc704\uce58, \ub465\uc9c0 \uc5ec\ubd80, \uc678\ubd80 \ub09c\uac04 \uc791\uc5c5 \uac00\ub2a5 \uc5ec\ubd80, \uc791\uc5c5 \uac00\ub2a5 \ubc94\uc704\ub97c \uc0c1\ub2f4 \uc804\uc5d0 \ud655\uc778\ud569\ub2c8\ub2e4.</p><p>\ubd84\ubcc0\xb7\ub465\uc9c0\xb7\uc791\uc5c5 \uac00\ub2a5 \ubc94\uc704 \uae30\uc900\uc73c\ub85c \uc815\ub9ac\ud569\ub2c8\ub2e4.</p></article><article class="journal-card"><span>\ud2b9\uc218\uccad\uc18c</span><h3>\ud2b9\uc218\uccad\uc18c \uc0c1\ub2f4 \uc804 \uc54c\ub824\uc8fc\uba74 \uc88b\uc740 \ub0b4\uc6a9</h3><p>\uc624\uc5fc \ubc94\uc704, \ub0c4\uc0c8 \uc815\ub3c4, \ud3d0\uae30\ubb3c \uc591, \ucd9c\uc785 \uac00\ub2a5 \uc2dc\uac04, \uc5d8\ub9ac\ubca0\uc774\ud130 \uc0ac\uc6a9 \uc5ec\ubd80\ub97c \uba3c\uc800 \ud655\uc778\ud558\uba74 \uc0c1\ub2f4\uc774 \ube68\ub77c\uc9d1\ub2c8\ub2e4.</p><p>\uc624\uc5fc \ubc94\uc704\uc640 \ucd9c\uc785 \uc870\uac74\uc744 \uae30\uc900\uc73c\ub85c \uc815\ub9ac\ud569\ub2c8\ub2e4.</p></article>'''
if '\ube44\ub458\uae30 \ud1f4\uce58 \uc804 \ud655\uc778\ud560 \uc0ac\ud56d' not in s:
    s=s.replace('</div></div></section>\n<section id="policy"',extra+'</div></div></section>\n<section id="policy"',1)

review_css = '''
/* REVIEW_TEXT_SWIPE */
.review-text-section{margin:34px auto 0;max-width:1100px;text-align:left}
.review-text-section h3{font-size:24px;margin:0 0 8px;color:#0f172a}
.review-text-lead{margin:0 0 16px;color:#64748b;line-height:1.7;font-size:15px}
.review-text-scroll{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 6px 18px;margin:0 -6px;scrollbar-width:none;cursor:grab;-webkit-overflow-scrolling:touch}
.review-text-scroll::-webkit-scrollbar{display:none}
.review-text-scroll:active{cursor:grabbing}
.review-text-card{flex:0 0 320px;scroll-snap-align:start;background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);text-align:left}
.review-text-card b{display:block;margin:0 0 12px;color:#0f172a;font-size:17px;line-height:1.45}
.review-text-card p{margin:0;color:#334155;line-height:1.72;font-size:16px;font-weight:800}
.review-text-hint{margin:0;color:#94a3b8;font-size:13px;font-weight:800}
@media(max-width:760px){.review-text-section{margin-top:28px}.review-text-card{flex-basis:82vw;max-width:340px;padding:20px}.review-text-card b{font-size:16px}.review-text-card p{font-size:15.5px}.review-text-hint{font-size:12px}}
'''.strip()

review_html = '''
<!-- REVIEW_TEXT_SWIPE_BLOCK_START -->
<section class="review-text-section" aria-label="텍스트 고객 후기">
  <h3>짧은 고객 후기</h3>
  <p class="review-text-lead">사진 후기 아래에 실제 후기 문구를 함께 정리했습니다.</p>
  <div class="review-text-scroll" aria-label="고객 후기 텍스트 슬라이드">
    <article class="review-text-card">
      <b>인천 입주청소 고객 후기</b>
      <p>“친절하게 설명해주시고 깨끗하게 해주셔서 감사합니다.”</p>
    </article>
    <article class="review-text-card">
      <b>부평 이사청소 고객 후기</b>
      <p>“사진으로 먼저 상담받을 수 있어서 편했어요.”</p>
    </article>
    <article class="review-text-card">
      <b>인천 비둘기 퇴치 고객 후기</b>
      <p>“설명 듣고 진행해서 걱정이 덜했어요.”</p>
    </article>
    <article class="review-text-card">
      <b>쓰레기집 청소 고객 후기</b>
      <p>“어디서부터 해야 할지 막막했는데 정리해주셔서 감사합니다.”</p>
    </article>
  </div>
  <p class="review-text-hint">옆으로 넘겨서 후기를 확인하실 수 있습니다.</p>
</section>
<!-- REVIEW_TEXT_SWIPE_BLOCK_END -->
'''.strip()

review_js = '''

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
'''.rstrip()

if '/* REVIEW_TEXT_SWIPE */' not in s:
    s=s.replace('</style>', review_css+'\n</style>', 1)

start='<!-- REVIEW_TEXT_SWIPE_BLOCK_START -->'
end='<!-- REVIEW_TEXT_SWIPE_BLOCK_END -->'
if start in s and end in s:
    a=s.index(start)
    b=s.index(end,a)+len(end)
    s=s[:a]+review_html+s[b:]
else:
    marker='\n    </div>\n  </section>\n<section id="journal"'
    review_pos=s.index('<div class="review-marquee"')
    insert_pos=s.index(marker, review_pos)
    s=s[:insert_pos]+'\n'+review_html+s[insert_pos:]

if '/* REVIEW_TEXT_DRAG */' not in s:
    s=s.replace('</script>', review_js+'\n</script>', 1)

p.write_text(s,encoding='utf-8')