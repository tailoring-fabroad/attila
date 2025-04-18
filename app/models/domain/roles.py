from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.domain.base_model import Base

users_to_roles = Table(
    "users_to_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, unique=True, nullable=False)  # 'CUSTOMER' / 'CONTRIBUTOR'
    
    users = relationship("User", secondary=users_to_roles, back_populates="roles")
