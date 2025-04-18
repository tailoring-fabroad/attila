from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.domain.base_model import Base
from app.models.domain.roles import users_to_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    bio = Column(String, default="")
    image = Column(String, nullable=True)

    roles = relationship("Role", secondary=users_to_roles, back_populates="users")
