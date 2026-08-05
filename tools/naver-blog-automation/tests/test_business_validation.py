"""7단계 테스트 2, 3: 정보형 사진 없음 / 작업사례형 전·중·후 배치."""
from models.giftclean_post import GiftCleanPostRequest, PhotoIn, PostType, ServiceType, PhotoGroup


def _base_kwargs(**overrides):
    kwargs = dict(
        post_type=PostType.INFO, service_type=ServiceType.HOARDING, region="서울 강동구",
        topic="쓰레기집 청소 비용", memo="현장 메모", main_keyword="쓰레기집 청소",
        cta_phrase="사진만 보내주셔도 상담 가능합니다.",
    )
    kwargs.update(overrides)
    return kwargs


def test_info_post_without_photos_is_valid():
    req = GiftCleanPostRequest(**_base_kwargs(post_type=PostType.INFO, photos=[]))
    assert req.validate_business_rules() == []


def test_case_post_without_photos_is_invalid():
    req = GiftCleanPostRequest(**_base_kwargs(post_type=PostType.CASE, photos=[]))
    errors = req.validate_business_rules()
    assert any("사진이 필요" in e for e in errors)


def test_case_post_photo_missing_group_is_invalid():
    photo = PhotoIn(data="AAAA", filename="a.jpg", group=None, order=0)
    req = GiftCleanPostRequest(**_base_kwargs(post_type=PostType.CASE, photos=[photo]))
    errors = req.validate_business_rules()
    assert any("그룹" in e for e in errors)


def test_photos_ordered_before_during_after():
    photos = [
        PhotoIn(data="A", filename="after1.jpg", group=PhotoGroup.AFTER, order=0),
        PhotoIn(data="B", filename="before2.jpg", group=PhotoGroup.BEFORE, order=1),
        PhotoIn(data="C", filename="during1.jpg", group=PhotoGroup.DURING, order=0),
        PhotoIn(data="D", filename="before1.jpg", group=PhotoGroup.BEFORE, order=0),
    ]
    req = GiftCleanPostRequest(**_base_kwargs(post_type=PostType.CASE, photos=photos))
    ordered = req.photos_ordered()
    filenames = [p.filename for p in ordered]
    assert filenames == ["before1.jpg", "before2.jpg", "during1.jpg", "after1.jpg"]
    assert req.validate_business_rules() == []


def test_nationwide_vs_metro_service_flag():
    special = GiftCleanPostRequest(**_base_kwargs(service_type=ServiceType.SPECIAL))
    move_in = GiftCleanPostRequest(**_base_kwargs(service_type=ServiceType.MOVE_IN))
    assert special.is_nationwide_service is True
    assert move_in.is_nationwide_service is False
