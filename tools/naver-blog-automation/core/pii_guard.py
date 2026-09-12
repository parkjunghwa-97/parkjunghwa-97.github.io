"""개인정보 노출 가능성 경고 유틸리티.

중요한 정직성 원칙: 이 모듈은 사진 '픽셀 내용'에서 얼굴·차량번호를 자동으로
인식하는 컴퓨터 비전 기능을 갖고 있지 않다(그런 기능이 있다고 말하지 않는다 —
요청사항 4단계 7번). 대신 두 가지만 한다:

1. 텍스트(파일명·본문·메모)에서 전화번호/주소/비밀번호처럼 보이는 패턴을
   정규식으로 찾아 경고한다 (기계적으로 확인 가능한 부분만).
2. 사진을 쓸 때마다 "얼굴/차량번호/주소/공동현관 비밀번호/전화번호가 보이는지
   직접 확인해달라"는 고정 체크리스트를 항상 사용자에게 보여준다(자동 탐지 아님,
   수동 확인 요청).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

PHONE_PATTERN = re.compile(r"01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}")
LANDLINE_PATTERN = re.compile(r"0(?:2|[3-6][1-5])[-.\s]?\d{3,4}[-.\s]?\d{4}")
PLATE_PATTERN = re.compile(r"\d{2,3}[가-힣]\d{4}")  # 예: 12가3456, 123가4567
DOORLOCK_HINT_PATTERN = re.compile(r"(공동현관|현관\s*비밀번호|도어락|출입\s*비밀번호)")
ADDRESS_HINT_PATTERN = re.compile(r"(\d+동\s*\d+호|\d+-\d+번지)")

# 사진을 하나라도 쓸 때마다 항상 노출하는 고정 안내문 — "자동 탐지"라고 주장하지 않는다.
MANUAL_PHOTO_CHECKLIST = (
    "사진에 다음이 보이는지 직접 확인해주세요 (자동 인식 기능은 아직 없습니다): "
    "① 사람 얼굴  ② 차량 번호판  ③ 상세 주소가 보이는 문서/우편물  "
    "④ 공동현관·도어락 비밀번호  ⑤ 전화번호가 적힌 메모/영수증. "
    "보이면 업로드 전 직접 가리거나 다른 사진으로 교체해주세요."
)


@dataclass
class PiiScanResult:
    has_warning: bool = False
    findings: list[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.has_warning = True
        self.findings.append(msg)


def scan_text(text: str, source_label: str = "본문") -> PiiScanResult:
    """텍스트에서 기계적으로 확인 가능한 개인정보 패턴을 찾는다."""
    result = PiiScanResult()
    if not text:
        return result
    if PHONE_PATTERN.search(text):
        result.add(f"{source_label}에 휴대폰 번호로 보이는 패턴이 있습니다.")
    if LANDLINE_PATTERN.search(text):
        result.add(f"{source_label}에 유선전화 번호로 보이는 패턴이 있습니다.")
    if PLATE_PATTERN.search(text):
        result.add(f"{source_label}에 차량 번호판으로 보이는 패턴이 있습니다.")
    if DOORLOCK_HINT_PATTERN.search(text):
        result.add(f"{source_label}에 공동현관/도어락 비밀번호 관련 언급이 있습니다.")
    if ADDRESS_HINT_PATTERN.search(text):
        result.add(f"{source_label}에 상세 주소(동/호/번지)로 보이는 패턴이 있습니다.")
    return result


def scan_filenames(filenames: list[str]) -> PiiScanResult:
    """파일명 자체에 개인정보가 노출된 경우(예: '010-1234-5678.jpg')를 찾는다."""
    result = PiiScanResult()
    for name in filenames:
        sub = scan_text(name, source_label=f"파일명 '{name}'")
        result.findings.extend(sub.findings)
        result.has_warning = result.has_warning or sub.has_warning
    return result


def full_scan(*, body_text: str = "", memo: str = "", filenames: Optional[list[str]] = None) -> PiiScanResult:
    """본문/메모/파일명을 종합해 한 번에 스캔한다. (사진 픽셀 내용은 스캔하지 않음 — 위 docstring 참고)"""
    result = PiiScanResult()
    for label, text in (("본문", body_text), ("메모", memo)):
        sub = scan_text(text, source_label=label)
        result.findings.extend(sub.findings)
        result.has_warning = result.has_warning or sub.has_warning
    if filenames:
        sub = scan_filenames(filenames)
        result.findings.extend(sub.findings)
        result.has_warning = result.has_warning or sub.has_warning
    return result
