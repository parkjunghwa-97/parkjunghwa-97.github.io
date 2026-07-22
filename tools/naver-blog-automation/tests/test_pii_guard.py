"""7단계 테스트 10: 개인정보 포함 파일명과 본문 경고 테스트."""
from core.pii_guard import full_scan, scan_filenames, MANUAL_PHOTO_CHECKLIST


def test_clean_text_has_no_warning():
    res = full_scan(body_text="쓰레기집 청소는 현장 상태에 따라 달라질 수 있습니다.", memo="일반 메모")
    assert res.has_warning is False
    assert res.findings == []


def test_phone_number_in_body_is_flagged():
    res = full_scan(body_text="상담 문의는 010-1234-5678 로 연락주세요.")
    assert res.has_warning is True
    assert any("휴대폰" in f for f in res.findings)


def test_phone_number_in_filename_is_flagged():
    res = scan_filenames(["010-1234-5678.jpg", "before1.jpg"])
    assert res.has_warning is True
    assert any("파일명" in f for f in res.findings)


def test_address_hint_is_flagged():
    res = full_scan(memo="101동 502호 화재 현장입니다.")
    assert res.has_warning is True
    assert any("주소" in f for f in res.findings)


def test_doorlock_hint_is_flagged():
    res = full_scan(body_text="공동현관 비밀번호는 미리 안내드립니다.")
    assert res.has_warning is True


def test_manual_checklist_does_not_claim_auto_detection():
    # 요청사항: "자동 모자이크 기능이 없다면 있다고 말하지 않는다"
    assert "자동" in MANUAL_PHOTO_CHECKLIST
    assert "아직 없습니다" in MANUAL_PHOTO_CHECKLIST
