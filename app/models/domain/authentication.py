from typing import Optional
from pydantic import BaseModel
from app.toolkit import security

class Authentication(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)

    class Config:
        orm_mode = True
