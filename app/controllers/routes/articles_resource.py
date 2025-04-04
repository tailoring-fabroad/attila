from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Response, UploadFile, Form, File
from starlette import status

from app.controllers.dependencies.authentication import get_current_user_authorizer
from app.controllers.dependencies.articles import (
    get_articles_filters, 
    check_article_modification_permissions, 
    get_article_by_slug_from_path,
)
from app.controllers.dependencies.database import get_repository
from app.repositories.data.articles import (ArticlesRepository, check_article_exists, get_slug_for_article)
from app.models.domain.articles import Article
from app.models.domain.users import User
from app.models.schemas.articles import (
    ArticlesFilters,
    ArticleForResponse,
    ResponseListArticles,
    RequestCreateArticle,
    RequestUpdateArticle,
    ResponseArticle,
)
from app.toolkit import response, constants, cloud_storage

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

@router.post("", name="Create Article", status_code=status.HTTP_201_CREATED)
async def create_new_article(
    title: str = Form(...),
    description: str = Form(...),
    body: str = Form(...),
    tagList: Optional[str] = Form(""),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user_authorizer()),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> ResponseArticle:
    slug = get_slug_for_article(title)

    if await check_article_exists(articles_repository, slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ARTICLE_ALREADY_EXISTS,
        )

    if not image.filename.endswith((".jpeg", ".jpg", ".png")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.INVALID_FILE_TYPE,
        )

    cloud_storage_image_url = await cloud_storage.upload_blob(image)

    article = await articles_repository.create_article(
        slug=slug,
        title=title,
        description=description,
        image=cloud_storage_image_url,
        body=body,
        author=current_user,
        tags=tagList.split(",") if tagList else [],
    )

    return await response.response_success(
        status_code=status.HTTP_201_CREATED,
        message="Article Created Successfully",
        data=article,
    )

@router.get("/{slug}", name="Get Article", dependencies=[Depends(check_article_modification_permissions)])
async def retrieve_article_by_slug(
    article: Article = Depends(get_article_by_slug_from_path),
) -> ResponseArticle:
    return await response.response_success(
        status_code= status.HTTP_200_OK, 
        message= "Success",
        data= ArticleForResponse.from_orm(article),
    )

@router.put("/{slug}", name="Update Article", dependencies=[Depends(check_article_modification_permissions)])
async def update_article_by_slug(
    article_update: RequestUpdateArticle = Body(..., embed=True, alias="article"),
    current_article: Article = Depends(get_article_by_slug_from_path),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> ResponseArticle:
    
    slug = get_slug_for_article(article_update.title) if article_update.title else None

    article = await articles_repository.update_article(
        article=current_article,
        slug=slug,
        **article_update.dict(),
    )

    return await response.response_success(
        status_code= status.HTTP_200_OK, 
        message= "Article Updated Successfully",
        data= article,
    )

@router.delete("/{slug}", name="Delete Article", dependencies=[Depends(check_article_modification_permissions)],
    status_code=status.HTTP_204_NO_CONTENT, response_class=Response,
)
async def delete_article_by_slug(
    article: Article = Depends(get_article_by_slug_from_path),
    articles_repository: ArticlesRepository = Depends(get_repository(ArticlesRepository)),
) -> None:
    await articles_repository.delete_article(article=article)