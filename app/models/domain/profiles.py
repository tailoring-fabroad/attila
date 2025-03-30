from typing import Optional

from app.models.domain.base_model import BaseModel

class Profile(BaseModel):
    username: str
    bio: str = ""
    image: Optional[str] = None
    following: bool = False
