from dataclasses import dataclass, field
from enum import Enum


class Visibility(Enum):
    PUBLIC = "공개"
    PRIVATE = "비공개"
    NEIGHBORS = "이웃공개"


@dataclass
class BlogPost:
    title: str = ""
    body: str = ""
    tags: list[str] = field(default_factory=list)
    image_paths: list[str] = field(default_factory=list)
    category: str = ""
    visibility: Visibility = Visibility.PUBLIC
    blog_id: str = ""
    section_image_map: dict = field(default_factory=dict)
    thumbnail_path: str = ""   # 썸네일 PNG 경로 (비어있으면 자동 생성 스킵)

    def validate(self) -> list[str]:
        errors = []
        if not self.title.strip():
            errors.append("제목을 입력해주세요")
        if not self.body.strip():
            errors.append("본문을 입력해주세요")
        if len(self.title) > 100:
            errors.append("제목은 100자 이하로 입력해주세요")
        return errors
