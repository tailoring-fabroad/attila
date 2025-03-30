from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.controllers.dependencies.authentication import get_current_user_authorizer
from app.controllers.dependencies.database import get_repository
from app.models.schemas.articles import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    ArticleForResponse,
    ResponseListArticles,
)
from app.repositories.data.articles import ArticlesRepository
from app.models.domain.users import User
from app.toolkit import response, constants

router = APIRouter()

@router.get("/feed", name="Get Articles for Feed", response_model=ResponseListArticles)
async def get_articles_for_feed(
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
    current_user: Optional[User] = Depends(get_current_user_authorizer(required=False)),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository))
) -> ResponseListArticles:

    articles = await articles_repository.get_articles_for_feed(
        limit=limit, 
        offset=offset,
        requested_user=current_user,
    )

    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.ARTICLE_DOES_NOT_EXIST_ERROR,
        )

    articles_for_response = [
        ArticleForResponse(**article.dict()) for article in articles
    ]

    return await response.response_success(
        status_code=status.HTTP_200_OK,
        message="Success",
        data=ResponseListArticles(
            articles=articles_for_response,
            articles_count=len(articles),
        )
    )