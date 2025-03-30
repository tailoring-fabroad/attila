from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.profiles import Profile
from app.models.domain.base_model import BaseModel

class Comment(IDModelMixin, DateTimeModelMixin, BaseModel):
    body: str
    author: Profile
