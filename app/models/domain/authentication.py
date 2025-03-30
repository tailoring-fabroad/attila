from app.models.domain.common import IDModelMixin, DateTimeModelMixin
from app.models.domain.users import User
from app.toolkit import security

class Authentication(IDModelMixin, DateTimeModelMixin, User):
    salt: str = ""
    hashed_password: str = ""
    
    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)
    
    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)