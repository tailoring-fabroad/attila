from typing import Optional
from fastapi import Query, Depends, HTTPException, Path
from starlette import status

from app.controllers.dependencies.authentication import get_current_user_authorizer
from app.controllers.dependencies.database import get_repository
from app.repositories.data.articles import check_user_can_modify_article
from app.repositories.errors import EntityDoesNotExist
from app.repositories.data.articles import ArticlesRepository
from app.models.domain.articles import Article
from app.models.domain.users import User
from app.toolkit import constants

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

async def get_article_by_slug_from_path(
    slug: str = Path(..., min_length=1),
    current_user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
    articles_repo: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> Article:
    try:
        return await articles_repo.get_article_by_slug(slug=slug, requested_user=current_user)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.ARTICLE_DOES_NOT_EXIST_ERROR,
        )

def check_article_modification_permissions(
    current_article: Article = Depends(get_article_by_slug_from_path),
    current_user: User = Depends(get_current_user_authorizer()),
) -> None:
    if not check_user_can_modify_article(current_article, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=constants.USER_IS_NOT_AUTHOR_OF_ARTICLE,
        )
