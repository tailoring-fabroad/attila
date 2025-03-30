from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from app.controllers.dependencies.database import get_repository
from app.models.schemas.articles import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    ArticleForResponse,
    ResponseListArticles,
)
from app.repositories.data.articles import ArticlesRepository
from app.toolkit.response import response_success
from app.toolkit import constants

router = APIRouter()

@router.get("/feed", name="Get Articles Feed", response_model=ResponseListArticles)
async def get_articles_for_feed(
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository))
) -> ResponseListArticles:

    articles = await articles_repository.get_articles_for_feed(limit=limit, offset=offset)

    if not articles:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=constants.ARTICLE_DOES_NOT_EXIST_ERROR,
        )

    articles_for_response = [
        ArticleForResponse(**article.dict()) for article in articles
    ]

    return await response_success(
        status_code=HTTP_200_OK,
        message="Success",
        data=ResponseListArticles(
            articles=articles_for_response,
            articles_count=len(articles),
        )
    )
