from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.domain.users import User
from app.models.domain.articles import Article