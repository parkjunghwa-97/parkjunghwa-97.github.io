"""기프트클린 블로그 글 입력/생성 데이터 모델.

웹 UI의 입력 폼 ↔ 글쓰기 엔진(core/giftclean_writer.py) 사이의 계약을 정의한다.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PostType(str, Enum):
    INFO = "정보형"
    CASE = "작업사례형"


class ServiceType(str, Enum):
    FIRE = "화재청소"
    HOARDING = "쓰레기집 청소"
    SPECIAL = "특수청소"
    BEREAVEMENT = "유품정리"
    LONELY_DEATH = "고독사 특수청소"
    PIGEON = "비둘기 퇴치"
    MOVE_IN = "입주청소"
    MOVING = "이사청소"
    RESIDENTIAL = "거주청소"
    OFFICE = "사무실·상가청소"
    FLOOD = "침수청소"
    WASTE = "폐기물 처리"


# 전국 출장 상담 가능 서비스 (요청사항 "공통 안내" 반영)
NATIONWIDE_SERVICES = {
    ServiceType.SPECIAL, ServiceType.HOARDING, ServiceType.BEREAVEMENT,
    ServiceType.LONELY_DEATH, ServiceType.FIRE, ServiceType.FLOOD, ServiceType.WASTE,
}
# 수도권 중심 운영 서비스
METRO_ONLY_SERVICES = {
    ServiceType.MOVE_IN, ServiceType.MOVING, ServiceType.RESIDENTIAL, ServiceType.PIGEON,
}


class PhotoGroup(str, Enum):
    BEFORE = "작업 전"
    DURING = "작업 중"
    AFTER = "작업 후"


class PhotoIn(BaseModel):
    """업로드된 사진 1장. order는 업로드 순서(그룹 내), group은 작업사례형에서만 사용."""
    media_type: str = "image/jpeg"
    data: str  # base64 (data URL 접두사 제외)
    filename: str = ""
    group: Optional[PhotoGroup] = None
    order: int = 0
    strip_gps: bool = True  # EXIF 위치정보 제거 여부 (기본 활성)


class GiftCleanPostRequest(BaseModel):
    # ── 필수 ──
    post_type: PostType
    service_type: ServiceType
    region: str = Field(..., min_length=1, description="주요 지역 (예: 서울 강동구)")
    topic: str = Field(..., min_length=1, description="핵심 주제")
    memo: str = Field(..., min_length=1, description="현장 또는 정보 메모")
    main_keyword: str = Field(..., min_length=1, description="핵심 키워드")
    sub_keywords: list[str] = Field(default_factory=list, description="보조 키워드")
    cta_phrase: str = Field(..., min_length=1, description="문의 유도 문구")
    photos: list[PhotoIn] = Field(default_factory=list)

    # ── 선택 ──
    area_pyeong: Optional[str] = None       # 평수
    work_date: Optional[str] = None          # 작업 날짜
    before_state: Optional[str] = None       # 작업 전 상태
    process_desc: Optional[str] = None       # 작업 과정
    result_desc: Optional[str] = None        # 작업 결과
    equipment: Optional[str] = None          # 사용 장비/약품
    customer_request: Optional[str] = None   # 고객 요청사항
    precautions: Optional[str] = None        # 주의사항
    homepage_url: Optional[str] = None
    kakao_channel_url: Optional[str] = None
    phone_number: Optional[str] = None

    def validate_business_rules(self) -> list[str]:
        """폼 규칙 검증 (필수값 존재 여부와 별개의 논리 검증)."""
        errors: list[str] = []
        if self.post_type == PostType.CASE and not self.photos:
            errors.append(
                "작업사례형 글은 최소 1장 이상의 사진이 필요합니다 "
                "(정보형은 사진 없이 작성 가능합니다)."
            )
        if self.post_type == PostType.CASE:
            for p in self.photos:
                if p.group is None:
                    errors.append(
                        f"작업사례형 사진 '{p.filename or '(이름없음)'}' 에 그룹(작업 전/중/후)이 지정되지 않았습니다."
                    )
        return errors

    @property
    def is_nationwide_service(self) -> bool:
        return self.service_type in NATIONWIDE_SERVICES

    def photos_ordered(self) -> list[PhotoIn]:
        """작업 전 → 작업 중 → 작업 후 순서로, 각 그룹 내에서는 업로드 순서를 유지."""
        order_map = {PhotoGroup.BEFORE: 0, PhotoGroup.DURING: 1, PhotoGroup.AFTER: 2}
        return sorted(
            self.photos,
            key=lambda p: (order_map.get(p.group, 99), p.order),
        )
