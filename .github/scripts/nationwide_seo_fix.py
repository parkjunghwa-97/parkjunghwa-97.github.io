from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

old_title = '기프트클린 대한청소만세 | 대전·세종 청소업체 · 입주청소 · 특수청소'
new_title = '기프트클린 대한청소만세 | 전국 출장 청소업체 · 입주청소 · 특수청소'
old_desc = '기프트클린 대한청소만세는 대전·세종·충청권 청소업체입니다. 입주청소, 이사청소, 사무실·상가청소, 쓰레기집 청소, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치 상담을 진행합니다.'
new_desc = '기프트클린 대한청소만세는 전국 출장 상담이 가능한 청소업체입니다. 대전·세종·충청권을 중심으로 입주청소, 이사청소, 사무실·상가청소, 쓰레기집 청소, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치 상담을 진행합니다.'
old_keywords = '대전 청소업체, 대전 입주청소, 대전 이사청소, 대전 사무실청소, 대전 상가청소, 대전 쓰레기집 청소, 대전 특수청소, 대전 유품정리, 대전 폐기물처리, 대전 비둘기퇴치, 세종 청소업체, 세종 입주청소, 세종 이사청소, 세종 특수청소, 청주 청소업체, 공주 청소업체, 계룡 청소업체, 논산 청소업체, 충청권 청소업체, 기프트클린, 대한청소만세'
new_keywords = '전국 청소업체, 전국 출장 청소, 전국 입주청소, 전국 이사청소, 전국 특수청소, 전국 고독사청소, 전국 유품정리, 전국 폐기물처리, 전국 비둘기퇴치, 대전 청소업체, 대전 입주청소, 대전 이사청소, 대전 특수청소, 세종 청소업체, 세종 입주청소, 세종 이사청소, 세종 특수청소, 청주 청소업체, 천안 청소업체, 아산 청소업체, 공주 청소업체, 계룡 청소업체, 논산 청소업체, 충청권 청소업체, 기프트클린, 대한청소만세'
old_service = '대전·세종·충청권 현장을 중심으로 사진 상담을 통해 현장 상태를 확인하고, 작업 범위와 예상 견적을 먼저 안내드립니다.'
new_service = '전국 출장 상담이 가능하며, 대전·세종·충청권 현장을 중심으로 사진 상담을 통해 현장 상태를 확인하고, 작업 범위와 예상 견적을 먼저 안내드립니다.'

text = text.replace(old_title, new_title)
text = text.replace(old_desc, new_desc)
text = text.replace(old_keywords, new_keywords)
text = text.replace(old_service, new_service, 1)

llms = Path('llms.txt')
if llms.exists():
    llms_text = llms.read_text(encoding='utf-8')
    llms_text = llms_text.replace('기프트클린 대한청소만세는 대전·세종·충청권 청소업체입니다.', '기프트클린 대한청소만세는 전국 출장 상담이 가능한 청소업체입니다. 대전·세종·충청권을 중심으로 입주청소, 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치 상담을 진행합니다.')
    llms.write_text(llms_text, encoding='utf-8')

for p in [Path('.github/scripts/nationwide_seo_fix.py'), Path('.github/workflows/nationwide-seo-fix.yml'), Path('run-nationwide-seo.txt')]:
    if p.exists():
        p.unlink()

index.write_text(text, encoding='utf-8')
