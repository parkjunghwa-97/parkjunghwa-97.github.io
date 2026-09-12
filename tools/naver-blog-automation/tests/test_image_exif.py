"""4단계: EXIF 위치정보 제거 옵션 테스트. 원본 바이트는 절대 변형하지 않는다(새 바이트만 반환)."""
import io

from PIL import Image

from core.image_exif import strip_gps, has_gps_data


def _gps_tagged_jpeg() -> bytes:
    img = Image.new("RGB", (10, 10), "red")
    exif = img.getexif()
    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = "N"
    gps_ifd[2] = (37.0, 33.0, 0.0)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def test_has_gps_data_detects_gps():
    assert has_gps_data(_gps_tagged_jpeg()) is True


def test_has_gps_data_false_for_plain_image():
    img = Image.new("RGB", (10, 10), "blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    assert has_gps_data(buf.getvalue()) is False


def test_strip_gps_removes_gps_tag():
    original = _gps_tagged_jpeg()
    stripped = strip_gps(original)
    assert has_gps_data(stripped) is False
    # 여전히 유효한 이미지여야 한다
    assert Image.open(io.BytesIO(stripped)).size == (10, 10)


def test_strip_gps_does_not_mutate_input_bytes_object():
    original = _gps_tagged_jpeg()
    original_copy = bytes(original)
    strip_gps(original)
    assert original == original_copy  # 원본 bytes 객체는 불변이며 그대로다


def test_strip_gps_invalid_input_falls_back_to_original():
    junk = b"not an image at all"
    assert strip_gps(junk) == junk
