from typing import List

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.profiles import Profile
from app.models.domain.base_model import BaseModel

class Article(IDModelMixin, DateTimeModelMixin, BaseModel):
    slug: str
    title: str
    description: str
    body: str
    image: str
    tags: List[str]
    author: Profile
    favorited: bool
    favorites_count: int