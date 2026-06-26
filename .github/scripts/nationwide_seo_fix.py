from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# remove checklist block if any
start=s.find('<div class="movein-check"')
if start!=-1:
    end=s.find('<div class="service-area"', start)
    if end!=-1:
        s=s[:start]+s[end:]
# rebuild FAQ/policy area cleanly
start=s.find('<section id="policy"')
end=s.find('<section id="partner"')
if start!=-1 and end!=-1:
    section='''<section id="policy" class="page">
    <div class="page-inner">
      <h2>자주 묻는 질문</h2>
      <p class="sub">상담 전 많이 묻는 내용을 정리했습니다.</p>
      <div class="faq-grid">
        <div class="faq-card"><b>사진만 보내도 견적 가능한가요?</b><p>네, 가능합니다. 현장 사진이나 영상을 보내주시면 오염도, 짐 유무, 폐기물 양, 작업 범위를 확인해 예상 견적을 안내드립니다.</p></div>
        <div class="faq-card"><b>당일 청소도 가능한가요?</b><p>일정이 맞는 경우 가능합니다. 작업 종류, 현장 상태, 이동 거리, 투입 인원에 따라 가능 여부가 달라질 수 있습니다.</p></div>
        <div class="faq-card"><b>추가 비용은 언제 발생하나요?</b><p>상담 당시 확인되지 않은 심한 오염, 폐기물 증가, 추가 공간, 추가 요청 작업 등이 있는 경우 사전 안내 후 진행합니다.</p></div>
      </div>
      <h2 class="policy-title">자세한 안내사항</h2>
      <p class="sub">예약, 결제, 작업 제한, 면책사항을 아코디언으로 확인하실 수 있습니다.</p>
      <div class="policy-list">
        <details><summary>폐기물 처리</summary><div class="policy-content">폐기물 처리 비용은 지역 및 품목에 따라 달라질 수 있습니다. 일부 품목은 별도 비용이 발생할 수 있습니다.</div></details>
        <details><summary>유품 및 귀중품 관련 안내</summary><div class="policy-content">귀중품, 현금, 중요 서류는 고객 또는 유가족이 사전에 직접 확인 및 보관해 주셔야 합니다.</div></details>
        <details><summary>결제 안내</summary><div class="policy-content">작업 완료 후 당일 결제를 원칙으로 하며 계좌이체 가능합니다. 현금영수증 및 세금계산서는 요청 시 발행 가능합니다.</div></details>
        <details><summary>작업 제한 및 안전정책</summary><div class="policy-content">작업자와 고객의 안전을 위해 위험 요소가 크거나 정상 진행이 어려운 현장은 일정 변경 또는 작업 제한을 안내할 수 있습니다.</div></details>
        <details><summary>면책사항</summary><div class="policy-content">건물 및 자재의 노후화, 기존 파손, 숨은 오염, 작업 후 사용 중 발생한 오염은 책임 범위에 포함되지 않을 수 있습니다.</div></details>
      </div>
    </div>
  </section>

  '''
    s=s[:start]+section+s[end:]
p.write_text(s,encoding='utf-8')
