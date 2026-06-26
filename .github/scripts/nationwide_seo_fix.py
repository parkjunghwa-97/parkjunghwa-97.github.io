from pathlib import Path
p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '<button class="nav-btn" onclick="showPage(\'contact\')">상담문의</button>'
new = '<button class="nav-btn" onclick="location.href=\'partner.html\'">파트너모집</button>\n      ' + old
if 'partner.html' not in s:
    s = s.replace(old, new, 1)
repls = {
    '더 자세한 안내사항 보기': '작업 전 안내사항 보기',
    '예약, 환불, 추가비용, A/S, 면책사항 등 작업 전 확인이 필요한 내용을 정리했습니다.': '예약금, 추가비용, A/S처럼 상담 전에 궁금한 부분을 미리 확인하실 수 있어요.',
    '예약 안내': '예약은 이렇게 진행돼요',
    '예약금 환불 기준': '예약금 환불은 이렇게 안내드려요',
    '현장 환불 기준': '작업 당일 취소·환불 안내',
    '사진 견적 안내': '사진 견적은 예상 견적이에요',
    '현장 상태 고지 의무': '현장 상태를 미리 알려주세요',
    '작업 범위': '작업 범위는 상담 기준으로 진행돼요',
    '추가 비용 발생 가능 항목': '추가비용이 생길 수 있는 경우',
    '고객 준비사항': '작업 전 준비해주시면 좋아요',
    '작업 결과 확인': '작업 후 확인 안내',
    '비대면 작업': '비대면 작업 안내',
    'A/S 정책': 'A/S 접수 안내',
    'A/S 제외 항목': 'A/S가 어려운 경우',
    '폐기물 처리': '폐기물 처리 비용 안내',
    '유품 및 귀중품 관련 안내': '유품·귀중품은 먼저 확인해주세요'
}
for a,b in repls.items():
    s = s.replace(a,b)
p.write_text(s, encoding='utf-8')
