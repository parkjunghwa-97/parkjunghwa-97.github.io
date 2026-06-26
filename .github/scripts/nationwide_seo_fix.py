from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('<div class="movein-check"')
if start!=-1:
    end=s.find('<div class="service-area"', start)
    if end!=-1:
        s=s[:start]+s[end:]
start=s.find('<section id="policy"')
end=s.find('<section id="partner"')
if start!=-1 and end!=-1:
    section='''<section id="policy" class="page">
    <div class="page-inner">
      <h2>자주 묻는 질문</h2>
      <div class="faq-grid">
        <div class="faq-card"><b>사진만 보내도 견적 가능한가요?</b><p>네, 가능합니다. 현장 사진이나 영상을 보내주시면 오염도, 짐 유무, 폐기물 양, 작업 범위를 확인해 예상 견적을 안내드립니다. 다만 사진에 보이지 않는 오염이나 추가 작업이 있는 경우 현장에서 금액이 변동될 수 있습니다.</p></div>
        <div class="faq-card"><b>당일 청소도 가능한가요?</b><p>일정이 맞는 경우 당일 작업도 가능합니다. 작업 종류, 현장 상태, 이동 거리, 투입 인원에 따라 가능 여부가 달라질 수 있어 상담 시 확인이 필요합니다.</p></div>
        <div class="faq-card"><b>입주청소와 이사청소는 다른가요?</b><p>입주청소는 새로 들어가기 전 빈 공간을 기준으로 진행하는 경우가 많고, 이사청소는 이전 거주 흔적이나 생활 오염이 남아 있는 경우가 많습니다. 현장 상태에 따라 작업 범위와 비용이 달라질 수 있습니다.</p></div>
        <div class="faq-card"><b>쓰레기집 청소도 가능한가요?</b><p>네, 가능합니다. 생활쓰레기, 음식물 쓰레기, 악취, 바닥 오염, 폐기물 양을 확인한 뒤 작업 범위와 예상 비용을 안내드립니다. 사진 확인 후 예상 견적 안내가 가능합니다.</p></div>
        <div class="faq-card"><b>비둘기 퇴치는 어떤 작업을 하나요?</b><p>현장 상태에 따라 분변 제거, 둥지 제거, 알·새끼 확인, 유입경로 차단막 설치 등을 진행합니다. 스카이 장비나 외부 작업이 필요한 경우 별도 안내드립니다.</p></div>
        <div class="faq-card"><b>추가 비용은 언제 발생하나요?</b><p>상담 당시 확인되지 않은 심한 오염, 폐기물 증가, 추가 공간, 추가 작업 요청, 장비 사용, 유료 주차비 등이 있는 경우 추가 비용이 발생할 수 있습니다. 추가 작업은 사전 안내 후 진행됩니다.</p></div>
        <div class="faq-card"><b>작업 후 A/S는 가능한가요?</b><p>작업 완료 후 3일 이내 접수 가능합니다. 사진 또는 영상으로 확인 후 작업 범위 내 미흡한 부분인지 확인하여 안내드립니다. 작업 완료 후 새로 발생한 오염이나 사용 중 발생한 오염은 A/S 대상에서 제외될 수 있습니다.</p></div>
      </div>

      <h2 class="policy-title">자세한 안내사항</h2>
      <p class="sub">예약, 환불, 작업 범위, A/S, 면책사항을 항목별로 확인하실 수 있습니다.</p>
      <div class="policy-list">
        <details><summary>예약 안내</summary><div class="policy-content"><ul><li>예약금 입금 확인 후 예약이 확정됩니다.</li><li>예약금은 최종 결제 금액에서 차감됩니다.</li><li>예약금 금액은 작업 규모, 서비스 종류, 일정에 따라 다르게 안내됩니다.</li></ul></div></details>
        <details><summary>예약금 환불 기준</summary><div class="policy-content"><ul><li>작업일 기준 7일 전 취소 : 예약금 100% 환불</li><li>작업일 기준 3~6일 전 취소 : 예약금 50% 환불</li><li>작업일 기준 2일 전 ~ 당일 취소 : 예약금 환불 불가</li></ul><p>※ 일정 변경은 작업일 기준 3일 전까지 1회 가능합니다.</p><p>※ 고객 연락 두절, 고객 부재, 현장 출입 불가, 주소 오기재 등의 경우 예약금은 환불되지 않습니다.</p><p>※ 천재지변, 사고, 입원 등 불가피한 사유는 협의 후 처리될 수 있습니다.</p></div></details>
        <details><summary>현장 환불 기준</summary><div class="policy-content"><ul><li>작업 시작 전 : 예약금 환불 기준 적용</li><li>작업 시작 후 : 환불 불가</li><li>고객 요청으로 작업이 중단된 경우 진행된 작업 범위에 대한 비용이 발생할 수 있습니다.</li><li>현장 상태가 상담 내용과 현저히 다른 경우 추가 비용 안내 후 고객이 작업을 거부할 경우 예약금은 환불되지 않습니다.</li></ul></div></details>
        <details><summary>사진 견적 안내</summary><div class="policy-content"><ul><li>사진 견적은 예상 견적이며 실제 현장 확인 후 금액이 변동될 수 있습니다.</li><li>사진에 확인되지 않은 오염, 폐기물, 추가 공간은 별도 안내 후 진행됩니다.</li></ul></div></details>
        <details><summary>현장 상태 고지 의무</summary><div class="policy-content"><ul><li>고객은 오염 상태, 폐기물, 반려동물, 해충 발생 여부 등을 사전에 알려주셔야 합니다.</li><li>미고지 사항으로 작업이 어려운 경우 일정 변경 또는 추가 비용이 발생할 수 있습니다.</li></ul></div></details>
        <details><summary>작업 범위</summary><div class="policy-content"><ul><li>상담 시 안내된 범위 내에서 작업이 진행됩니다.</li><li>추가 작업 요청 시 별도 비용이 발생할 수 있습니다.</li><li>현장 상태에 따라 작업 시간 및 인원이 변경될 수 있습니다.</li></ul></div></details>
        <details><summary>추가 비용 발생 가능 항목</summary><div class="policy-content"><ul><li>상담 내용과 다른 오염 상태</li><li>과도한 폐기물 발생</li><li>추가 공간 발생</li><li>추가 작업 요청</li><li>사다리차 및 스카이 장비 사용</li><li>폐기물 처리 비용</li><li>유료 주차비</li><li>특수 약품 및 장비 사용</li></ul></div></details>
        <details><summary>고객 준비사항</summary><div class="policy-content"><ul><li>귀중품, 현금, 중요 서류는 사전에 보관 부탁드립니다.</li><li>파손 우려 물품은 사전 이동 부탁드립니다.</li><li>반려동물은 안전한 공간에 분리 부탁드립니다.</li></ul></div></details>
        <details><summary>작업 결과 확인</summary><div class="policy-content"><ul><li>작업 완료 후 고객 확인을 원칙으로 합니다.</li><li>고객 확인 후 작업 종료 시 작업 결과에 동의한 것으로 간주합니다.</li></ul></div></details>
        <details><summary>비대면 작업</summary><div class="policy-content"><ul><li>비대면 작업 시 사진 및 영상으로 결과를 전달해 드립니다.</li><li>비대면 작업 완료 후에는 전달된 결과물을 기준으로 작업이 종료됩니다.</li></ul></div></details>
        <details><summary>A/S 정책</summary><div class="policy-content"><ul><li>작업 완료 후 3일 이내 접수 가능합니다.</li><li>사진 또는 영상 확인 후 A/S 여부를 안내합니다.</li><li>작업 범위 내 미흡한 청소</li><li>작업 누락 부위</li><li>작업 전 안내된 범위 내 보완 요청</li></ul></div></details>
        <details><summary>A/S 제외 항목</summary><div class="policy-content"><ul><li>작업 완료 후 발생한 오염</li><li>고객 사용 중 발생한 오염</li><li>가구, 가전제품 이동 후 발견된 오염</li><li>건물 및 자재의 노후화</li><li>변색, 부식, 백화 현상</li><li>기존 스크래치 및 숨은 하자</li><li>작업 전부터 존재하던 파손</li><li>곰팡이 재발</li><li>비둘기 재유입</li></ul><p>※ 비둘기 재유입의 경우 시공 문제로 확인되는 경우에 한하여 별도 확인 후 A/S가 진행될 수 있습니다.</p><p>※ 새로운 유입경로 발생, 건물 구조 변경, 외부 환경 변화 등으로 인한 재유입은 A/S 대상에서 제외됩니다.</p><p>※ 건물 구조상 완전한 차단이 어려운 경우가 있을 수 있으며, 이에 따른 재유입은 A/S 대상에서 제외됩니다.</p></div></details>
        <details><summary>폐기물 처리</summary><div class="policy-content"><ul><li>폐기물 처리 비용은 지역 및 품목에 따라 달라질 수 있습니다.</li><li>냉장고, 세탁기, 매트리스 등 일부 품목은 별도 비용이 발생할 수 있습니다.</li></ul></div></details>
        <details><summary>유품 및 귀중품 관련 안내</summary><div class="policy-content"><p>유품, 귀중품, 현금, 귀금속, 통장, 신분증, 중요 서류 등은 고객 또는 유가족이 사전에 직접 확인 및 보관해 주셔야 합니다.</p><p>대한청소만세는 고객이 지정한 작업 범위 내에서 작업을 진행하며, 미확인 유품 및 귀중품의 분실, 훼손, 누락에 대한 책임을 지지 않습니다.</p><p>유품정리 서비스의 경우에도 귀중품, 현금, 중요 서류는 작업 전 고객 또는 유가족이 우선 확인하는 것을 권장드립니다.</p><p>작업 중 발견되는 유품 및 귀중품은 고객에게 안내할 수 있으나, 보관·감정·분류 의무는 없습니다.</p></div></details>
        <details><summary>결제 안내</summary><div class="policy-content"><ul><li>작업 완료 후 당일 결제를 원칙으로 합니다.</li><li>계좌이체 가능합니다.</li><li>현금영수증 및 세금계산서는 요청 시 발행 가능합니다.</li><li>추가 작업 발생 시 사전 안내 후 진행합니다.</li></ul></div></details>
        <details><summary>작업 제한 및 안전정책</summary><div class="policy-content"><p>대한청소만세는 작업자와 고객의 안전을 최우선으로 합니다.</p><ul><li>전문 수리 및 보수 작업</li><li>도배, 장판, 전기, 설비 공사</li><li>위험물 처리</li><li>법적 허가가 필요한 작업</li><li>천재지변</li><li>폭우, 강풍, 폭설 등 기상 악화</li><li>장비 고장 또는 장비 사용 불가 상황</li><li>추락, 붕괴, 감전 등 안전사고 위험</li><li>작업자 또는 현장의 안전에 중대한 위험이 있다고 판단되는 경우</li><li>관계기관 통제 또는 출입 제한</li><li>기타 정상적인 작업 진행이 어렵다고 판단되는 상황</li></ul><p>위와 같은 상황이 발생할 경우 고객과 우선 일정 변경을 협의합니다.</p><p>일정 변경이 어렵거나 작업 진행이 불가능한 경우 예약금은 전액 환불됩니다.</p><p>다만 고객 미고지 사항, 현장 상태 상이, 현장 위험요소 발견, 고객 요청에 의한 작업 중단 등으로 인해 작업이 중단되는 경우에는 진행된 작업 범위에 대한 비용이 발생할 수 있습니다.</p><p>안전 확보가 어려운 상황에서 무리하게 작업을 진행하여 발생할 수 있는 사고를 예방하기 위해 작업을 제한 또는 중단할 수 있습니다.</p></div></details>
        <details><summary>면책사항</summary><div class="policy-content"><p>다음 사항은 대한청소만세의 책임 범위에 포함되지 않습니다.</p><ul><li>건물 및 자재의 노후화로 인한 손상, 변색, 부식</li><li>기존 하자 및 숨은 하자</li><li>작업 전부터 존재하던 파손</li><li>악취의 완전 제거가 어려운 경우</li><li>곰팡이 재발</li><li>비둘기 재유입</li><li>작업 완료 후 고객 사용 중 발생한 오염</li><li>자재 노후화로 인해 작업 과정에서 발생할 수 있는 예기치 못한 손상</li><li>고객이 직접 이동 또는 보관한 물품의 분실, 훼손</li></ul><p>※ 대한청소만세는 작업 전 확인 가능한 범위 내에서 작업을 진행하나, 건물 및 자재의 상태, 오염도 및 현장 환경에 따라 결과가 달라질 수 있습니다.</p></div></details>
      </div>
    </div>
  </section>

  '''
    s=s[:start]+section+s[end:]
p.write_text(s,encoding='utf-8')
