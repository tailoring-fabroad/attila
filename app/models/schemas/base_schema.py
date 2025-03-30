from app.models.domain.base_model import BaseModel

class BaseSchema(BaseModel):
    class Config(BaseModel.Config):
        orm_mode = True
