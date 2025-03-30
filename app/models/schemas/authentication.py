from pydantic import BaseModel, EmailStr
from app.models.schemas.base_schema import BaseSchema

class RequestLogin(BaseSchema):
    email: EmailStr
    password: str

class RequestRegister(BaseSchema):
    username: str
    email: EmailStr
    password: str

class ResponseAuthentication(BaseSchema):
    token: str
