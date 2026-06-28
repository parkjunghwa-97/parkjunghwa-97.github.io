from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Existing Korean copy cleanups kept idempotent.
s = s.replace('현장일지', '현장기록')
s = s.replace('작업사례 템플릿 보기', '현장기록 보기')
s = s.replace('<p class="sub">실제 현장별 작업 내용과 정보성 콘텐츠를 지역, 서비스, 작업 범위 중심으로 정리하는 공간입니다.</p>', '')
s = s.replace('<a href="/cases/">체크리스트 보기</a>', '<p>입주 전 확인 기준을 항목별로 정리하는 정보형 글입니다.</p>')
s = s.replace('<a href="/cases/">사진상담 기준 보기</a>', '<p>사진상담 전에 필요한 사진 기준을 정리하는 글입니다.</p>')
s = s.replace('<a href="/cases/">현장기록 보기</a>', '<p>실제 현장 기준으로 작업 범위를 정리하는 글입니다.</p>')

extra = '''<article class="journal-card"><span>비둘기 퇴치</span><h3>비둘기 퇴치 전 확인할 사항</h3><p>분변 위치, 둥지 여부, 외부 난간 작업 가능 여부, 작업 가능 범위를 상담 전에 확인합니다.</p><p>분변·둥지·작업 가능 범위 기준으로 정리합니다.</p></article><article class="journal-card"><span>특수청소</span><h3>특수청소 상담 전 알려주면 좋은 내용</h3><p>오염 범위, 냄새 정도, 폐기물 양, 출입 가능 시간, 엘리베이터 사용 여부를 먼저 확인하면 상담이 빨라집니다.</p><p>오염 범위와 출입 조건을 기준으로 정리합니다.</p></article>'''
if '비둘기 퇴치 전 확인할 사항' not in s:
    s = s.replace('</div></div></section>\n<section id="policy"', extra + '</div></div></section>\n<section id="policy"', 1)

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

review_js_body = '''
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
'''.strip()

# Remove the earlier misplaced drag script if it was inserted into the JSON-LD script.
old_review_js = '''

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
s = s.replace(old_review_js, '')

if '/* REVIEW_TEXT_SWIPE */' not in s:
    s = s.replace('</style>', review_css + '\n</style>', 1)

start = '<!-- REVIEW_TEXT_SWIPE_BLOCK_START -->'
end = '<!-- REVIEW_TEXT_SWIPE_BLOCK_END -->'
if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + review_html + s[b:]
else:
    marker = '\n    </div>\n  </section>\n<section id="journal"'
    review_pos = s.index('<div class="review-marquee"')
    insert_pos = s.index(marker, review_pos)
    s = s[:insert_pos] + '\n' + review_html + s[insert_pos:]

if '/* REVIEW_TEXT_DRAG */' not in s:
    s = s.replace('</body>', '<script>\n' + review_js_body + '\n</script>\n</body>', 1)

p.write_text(s, encoding='utf-8')
