from pathlib import Path
import re
p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '<button class="nav-btn" onclick="showPage(\'contact\')">상담문의</button>'
new = '<button class="nav-btn" onclick="location.href=\'partner.html\'">파트너모집</button>\n      ' + old
if 'partner.html' not in s:
    s = s.replace(old, new, 1)
intro = '\n        <p class="more-info-intro">예약금, 추가비용, A/S처럼<br>상담 전에 궁금한 부분을 미리 확인하기</p>'
s = re.sub(r'\n\s*<p class="more-info-intro">.*?</p>', '', s, count=1, flags=re.S)
s = s.replace('        <summary>작업 전 안내사항 보기</summary>', '        <summary>작업 전 안내사항 보기</summary>' + intro, 1)
fixes = {
    '작업 범위는 상담 기준으로 진행돼요 내': '작업 범위 내',
    '작업 범위는 상담 기준으로 진행돼요에 대한': '작업 범위에 대한',
    '예약금 환불은 이렇게 안내드려요 적용': '예약금 환불 기준 적용',
    '비대면 작업 안내 시': '비대면 작업 시',
    '비대면 작업 안내 완료 후에는': '비대면 작업 완료 후에는',
    '폐기물 처리 비용 안내 비용': '폐기물 처리 비용'
}
for a,b in fixes.items():
    s = s.replace(a,b)
p.write_text(s, encoding='utf-8')
