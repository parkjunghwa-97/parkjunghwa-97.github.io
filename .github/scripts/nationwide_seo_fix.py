from pathlib import Path
import re
p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '<button class="nav-btn" onclick="showPage(\'contact\')">상담문의</button>'
new = '<button class="nav-btn" onclick="location.href=\'partner.html\'">파트너모집</button>\n      ' + old
if 'partner.html' not in s:
    s = s.replace(old, new, 1)
s = re.sub(r'\n\s*<p class="more-info-intro">.*?</p>', '', s, count=1, flags=re.S)
repls = {
    '<summary>예약은 이렇게 진행돼요</summary>': '<summary>예약 안내</summary>',
    '<summary>예약금 환불은 이렇게 안내드려요</summary>': '<summary>예약금 환불 기준</summary>',
    '<summary>작업 당일 취소·환불 안내</summary>': '<summary>현장 환불 기준</summary>',
    '<summary>사진 견적은 예상 견적이에요</summary>': '<summary>사진 견적 안내</summary>',
    '<summary>현장 상태를 미리 알려주세요</summary>': '<summary>현장 상태 고지 의무</summary>',
    '<summary>작업 범위는 상담 기준으로 진행돼요</summary>': '<summary>작업 범위</summary>',
    '<summary>추가비용이 생길 수 있는 경우</summary>': '<summary>추가 비용 발생 가능 항목</summary>',
    '<summary>작업 전 준비해주시면 좋아요</summary>': '<summary>고객 준비사항</summary>',
    '<summary>작업 후 확인 안내</summary>': '<summary>작업 결과 확인</summary>',
    '<summary>비대면 작업 안내</summary>': '<summary>비대면 작업</summary>',
    '<summary>A/S 접수 안내</summary>': '<summary>A/S 정책</summary>',
    '<summary>A/S가 어려운 경우</summary>': '<summary>A/S 제외 항목</summary>',
    '<summary>폐기물 처리 비용 안내</summary>': '<summary>폐기물 처리</summary>',
    '<summary>유품·귀중품은 먼저 확인해주세요</summary>': '<summary>유품 및 귀중품 관련 안내</summary>'
}
for a,b in repls.items():
    s = s.replace(a,b)
fixes = {
    '작업 범위는 상담 기준으로 진행돼요 내': '작업 범위 내',
    '작업 범위는 상담 기준으로 진행돼요에 대한': '작업 범위에 대한',
    '예약금 환불은 이렇게 안내드려요 적용': '예약금 환불 기준 적용',
    '비대면 작업 안내 시': '비대면 작업 시',
    '비대면 작업 안내 완료 후에는': '비대면 작업 완료 후에는',
    '폐기물 처리 비용 안내 비용': '폐기물 처리 비용',
    '폐기물 처리 비용 안내</b>': '폐기물 처리</b>',
    '오염도와 작업 범위는 상담 기준으로 진행돼요 확인': '오염도와 작업 범위 확인'
}
for a,b in fixes.items():
    s = s.replace(a,b)
mobile_css = '''
    /* MOBILE_NAV_FLOW_FIX */
    @media(max-width:760px){
      .top-nav{position:sticky;top:0;left:auto;right:auto}
      .page,.hero{padding-top:36px}
      #portfolio{padding-top:36px}
    }
'''
if 'MOBILE_NAV_FLOW_FIX' not in s:
    s = s.replace('\n  </style>', mobile_css + '\n  </style>', 1)
p.write_text(s, encoding='utf-8')
