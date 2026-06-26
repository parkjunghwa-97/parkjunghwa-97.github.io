from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('현장일지','현장기록')
s=s.replace('작업사례 템플릿 보기','현장기록 보기')
s=s.replace('실제 현장 기록을 지역, 서비스, 작업 범위 중심의 텍스트로 쌓아가는 공간입니다.','실제 현장별 작업 내용과 정보성 콘텐츠를 지역, 서비스, 작업 범위 중심으로 정리하는 공간입니다.')
insert='<article class="journal-card"><span>정보형</span><h3>신축 입주 전 체크할 30가지</h3><p>창틀, 주방, 욕실, 수납장처럼 입주 전후에 함께 확인하면 좋은 항목을 정리합니다.</p><a href="/cases/">체크리스트 보기</a></article><article class="journal-card"><span>정보형</span><h3>입주청소 사진상담 전 보내면 좋은 사진</h3><p>전체 구조, 창틀, 주방, 욕실, 베란다, 오염 부위를 먼저 보내주시면 작업 범위 안내가 더 정확해집니다.</p><a href="/cases/">사진상담 기준 보기</a></article>'
if '신축 입주 전 체크할 30가지' not in s:
    s=s.replace('<div class="journal-grid">','<div class="journal-grid">'+insert,1)
# 메뉴 이동도 브라우저 뒤로가기가 되도록 처리
if 'function showPage(id){' in s:
    s=s.replace('function showPage(id){','function showPage(id, fromHistory){',1)
if "history.pushState({page:id}" not in s:
    s=s.replace("      window.scrollTo({top:0,behavior:'auto'});\n    }", "      if(!fromHistory && window.location.hash !== '#'+id){history.pushState({page:id},'', '#'+id);}\n      window.scrollTo({top:0,behavior:'auto'});\n    }", 1)
s=s.replace("if(home){\n            home.classList.add('active');\n          }", "if(home && !location.hash){\n            home.classList.add('active');\n          }")
if "window.addEventListener('popstate'" not in s:
    extra="""
    window.addEventListener('popstate', function(){
      const id=(location.hash||'#home').replace('#','');
      if(document.getElementById(id)){showPage(id,true);}
    });
    document.addEventListener('DOMContentLoaded', function(){
      const id=(location.hash||'').replace('#','');
      if(id && document.getElementById(id)){showPage(id,true);}
    });
"""
    s=s.replace('</script>', extra+'</script>',1)
p.write_text(s,encoding='utf-8')
