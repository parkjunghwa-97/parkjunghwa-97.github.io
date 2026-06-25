from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

text = text.replace('기프트클린 대한청소만세 | 대전 청소업체 · 입주청소 · 특수청소 · 유품정리', '기프트클린 대한청소만세 | 대전·세종 청소업체 · 입주청소 · 특수청소')
text = text.replace('기프트클린 대한청소만세는 대전·세종·충청권 중심의 청소업체입니다.', '기프트클린 대한청소만세는 대전·세종·충청권 청소업체입니다.')
text = text.replace('대전 청소업체, 세종 청소업체, 충청권 청소업체, 입주청소, 이사청소, 사무실청소, 상가청소, 쓰레기집 청소, 특수청소, 고독사 특수청소, 유품정리, 폐기물 처리, 비둘기 퇴치, 기프트클린, 대한청소만세', '대전 청소업체, 대전 입주청소, 대전 이사청소, 대전 사무실청소, 대전 상가청소, 대전 쓰레기집 청소, 대전 특수청소, 대전 유품정리, 대전 폐기물처리, 대전 비둘기퇴치, 세종 청소업체, 세종 입주청소, 세종 이사청소, 세종 특수청소, 청주 청소업체, 공주 청소업체, 계룡 청소업체, 논산 청소업체, 충청권 청소업체, 기프트클린, 대한청소만세')
text = text.replace('{"@type": "Country", "name": "대한민국"}', '{"@type": "City", "name": "청주시"}')
text = text.replace('"@type": "Country",\n                  "name": "대한민국"', '"@type": "City",\n                  "name": "청주시"')
text = text.replace('사진 상담을 통해 현장 상태를 확인하고, 작업 범위와 예상 견적을 먼저 안내드립니다.', '대전·세종·충청권 현장을 중심으로 사진 상담을 통해 현장 상태를 확인하고, 작업 범위와 예상 견적을 먼저 안내드립니다.', 1)

llms = Path('llms.txt')
if llms.exists():
    llms_text = llms.read_text(encoding='utf-8')
    llms_text = llms_text.replace('기프트클린 대한청소만세는 대전·세종·충청권 중심의 청소업체입니다.', '기프트클린 대한청소만세는 대전·세종·충청권 청소업체입니다.')
    llms.write_text(llms_text, encoding='utf-8')

index.write_text(text, encoding='utf-8')
