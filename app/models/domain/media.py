from typing import List, Optional
from uuid import UUID

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.base_model import BaseModel
from app.models.domain.profiles import Profile

class Media(IDModelMixin, DateTimeModelMixin, BaseModel):
    asset_id: UUID
    type: str  # image | video | audio
    title: Optional[str]
    description: Optional[str]
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    tags: List[str] = []
    author: Optional[Profile]
    favorited: bool = False
    favorites_count: int = 0

class MediaImage(Media):
    width: int
    height: int
    format: str  # jpg | jpeg | eps

class MediaVideo(Media):
    resolution: str
    duration_seconds: int
    format: str  # mp4 | mov

class MediaAudio(Media):
    duration_seconds: int
    bitrate_kbps: int
    format: str # mp3
