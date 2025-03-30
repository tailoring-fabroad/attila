from typing import Optional
from fastapi import Query

from app.models.schemas.articles import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    ArticlesFilters,
)

def get_articles_filters(
    tag: Optional[str] = None,
    author: Optional[str] = None,
    favorited: Optional[str] = None,
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> ArticlesFilters:
    return ArticlesFilters(
        tag=tag,
        author=author,
        favorited=favorited,
        limit=limit,
        offset=offset,
    )