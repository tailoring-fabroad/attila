from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.controllers.dependencies.authentication import get_current_user_authorizer
from app.controllers.dependencies.articles import get_articles_filters
from app.controllers.dependencies.database import get_repository
from app.repositories.data.articles import ArticlesRepository
from app.models.domain.users import User
from app.models.schemas.articles import (
    ArticlesFilters,
    ArticleForResponse,
    ResponseListArticles,
)
from app.toolkit import response, constants

router = APIRouter()

@router.get("", name="Get Articles", response_model=ResponseListArticles)
async def get_articles(
    articles_filters: ArticlesFilters = Depends(get_articles_filters),
    current_user: Optional[User] = Depends(get_current_user_authorizer(required=True)),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> ResponseListArticles:
    
    articles = await articles_repository.filter_articles(
        tag=articles_filters.tag,
        author=articles_filters.author,
        favorited=articles_filters.favorited,
        limit=articles_filters.limit,
        offset=articles_filters.offset,
        requested_user=current_user,
    )

    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.ARTICLE_DOES_NOT_EXIST_ERROR,
        )

    articles_for_response = [
        ArticleForResponse.from_orm(article) for article in articles
    ]

    return await response.response_success(
        status_code=status.HTTP_200_OK,
        message="Success",
        data=ResponseListArticles(
            articles=articles_for_response,
            articles_count=len(articles),
        )
    )