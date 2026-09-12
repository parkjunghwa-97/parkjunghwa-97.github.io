"""EXIF 위치정보(GPS) 제거 유틸리티.

요청사항: "원본 사진 파일을 임의로 삭제하거나 덮어쓰지 않는다" + "EXIF 위치정보
제거 옵션을 제공한다". 그래서 이 모듈은 항상 새 바이트를 반환할 뿐, 원본 파일을
열람 전용(read-only)으로만 다루고 절대 write-back 하지 않는다.
"""
from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

# JPEG EXIF의 GPS IFD 태그 번호
_GPS_TAG_ID = 0x8825


def strip_gps(image_bytes: bytes) -> bytes:
    """이미지 바이트에서 GPS EXIF만 제거한 '새' 바이트를 반환한다.

    실패하면(포맷 미지원, Pillow 없음 등) 원본 바이트를 그대로 반환하고 경고 로그를 남긴다
    (원본을 절대 훼손하지 않는다는 원칙이 EXIF 제거 성공보다 우선한다).
    """
    try:
        from PIL import Image
    except ImportError:
        logger.warning("Pillow가 설치되어 있지 않아 EXIF 제거를 건너뜁니다 (원본 그대로 사용).")
        return image_bytes

    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif = img.getexif()
        # 주의: exif.get_ifd(GPS)를 '삭제 이후'에 호출하면 Pillow가 빈 GPS 서브-IFD를
        # 내부 캐시에 다시 등록해버려 save() 시 GPS 태그가 되살아난다(실제로 확인된 버그).
        # 그래서 메인 GPS 포인터 태그(0x8825)를 지우는 것 하나로 끝내고, get_ifd는 호출하지 않는다.
        if _GPS_TAG_ID in exif:
            del exif[_GPS_TAG_ID]

        out = io.BytesIO()
        save_format = img.format or "JPEG"
        img.save(out, format=save_format, exif=exif)
        return out.getvalue()
    except Exception as exc:
        logger.warning(f"EXIF 제거 실패(원본 그대로 사용): {exc}")
        return image_bytes


def has_gps_data(image_bytes: bytes) -> bool:
    """GPS EXIF 포함 여부만 확인(제거하지 않음) — UI 경고 배지용."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        exif = img.getexif()
        return _GPS_TAG_ID in exif
    except Exception:
        return False
