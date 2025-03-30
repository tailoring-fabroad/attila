from typing import Optional

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.base_model import BaseModel

class User(BaseModel):
    username: str
    email: str
    bio: str = ""
    image: Optional[str] = None
