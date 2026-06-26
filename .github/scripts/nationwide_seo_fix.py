from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = re.sub(r'(· 쓰레기집 청소)(?: · 쓰레기집 청소)+', r'\1', s)
s = s.replace('폐기물 처리 비용 안내', '폐기물 처리')
s = s.replace('작업 범위는 상담 기준으로 진행돼요를 확인해 예상 견적을 안내드립니다.', '작업 범위를 확인해 예상 견적을 안내드립니다.')
s = s.replace('<b>사업장 기준</b>', '<b>사업장</b>')

def lazy_img(m):
    tag = m.group(0)
    if 'intro-logo' not in tag and 'loading=' not in tag:
        tag = tag.replace('<img', '<img loading="lazy"', 1)
    if 'intro-logo' not in tag and 'decoding=' not in tag:
        tag = tag.replace('<img', '<img decoding="async"', 1)
    return tag
s = re.sub(r'<img\b[^>]*>', lazy_img, s)

review = '<div class="review-text-section"><h3>후기 텍스트 요약</h3><p>이미지 후기는 유지하고, 검색엔진이 읽을 수 있게 후기를 텍스트로도 정리합니다.</p><div class="review-text-grid"><article><b>입주청소 후기</b><p>지역, 서비스 종류, 현장 상태, 작업 범위를 함께 기록합니다.</p></article><article><b>정리 청소 후기</b><p>오염 상태, 작업 범위, 상담 내용을 텍스트로 남깁니다.</p></article><article><b>퇴치 작업 후기</b><p>현장 상태와 작업 내용을 짧은 문장으로 정리합니다.</p></article></div></div>'
s = re.sub(r'\s*<div class="review-text-section".*?</div>\s*', '', s, flags=re.S)
s = s.replace('<section id="journal"', review + '\n<section id="journal"', 1)

css = '/* REVIEW_TEXT_SIMPLE */.review-text-section{margin:30px auto 0;max-width:980px;text-align:left}.review-text-section h3{font-size:24px;margin:0 0 8px;color:#0f172a}.review-text-section p{color:#64748b;line-height:1.7}.review-text-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}.review-text-grid article{background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08)}.review-text-grid b{display:block;margin-bottom:8px;color:#0f172a}'
s = re.sub(r'\n\s*/\* REVIEW_TEXT_SIMPLE \*/.*?(?=\n\s*/\* MOBILE_NAV_FLOW_FIX \*/|\n\s*/\* PARTNER_SECTION \*/|\n\s*</style>)', '\n', s, flags=re.S)
s = s.replace('    /* MOBILE_NAV_FLOW_FIX */', css + '\n    /* MOBILE_NAV_FLOW_FIX */', 1) if '    /* MOBILE_NAV_FLOW_FIX */' in s else s.replace('</style>', css + '</style>', 1)

p.write_text(s, encoding='utf-8')
