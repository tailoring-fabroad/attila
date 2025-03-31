from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.schemas.base_schema import BaseSchema
from app.models.domain.articles import Article

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0

class ArticleForResponse(BaseSchema, Article):
    tags: List[str] = Field(..., alias="tag_list")

class ResponseArticle():
    article: ArticleForResponse

class ResponseListArticles(BaseSchema):
    articles: List[ArticleForResponse]
    articles_count: int

class ArticlesFilters(BaseModel):
    tag: Optional[str] = None
    author: Optional[str] = None
    favorited: Optional[str] = None
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)

class RequestCreateArticle(BaseSchema):
    title: str
    description: str
    body: str
    image: str
    tags: List[str] = Field([], alias="tagList")

class RequestUpdateArticle(BaseSchema):
    title: str
    description: str
    body: str
    image: str
    # tags: List[str] = Field([], alias="tagList")