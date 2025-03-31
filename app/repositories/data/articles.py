from typing import List, Optional, Union, Sequence

from asyncpg import Connection, Record 
from pypika import Query
from slugify import slugify

from app.models.domain.profiles import Profile
from app.repositories.errors import EntityDoesNotExist
from app.repositories.queries.queries import queries
from app.repositories.data.base import BaseRepository
from app.repositories.queries.tables import (
    Parameter,
    articles,
    articles_to_tags,
    favorites,
    tags as tags_table,
    users,
)
from app.models.domain.articles import Article
from app.models.domain.users import User
from app.repositories.data.profiles import ProfilesRepository

AUTHOR_USERNAME_ALIAS = "author_username"
SLUG_ALIAS = "slug"

CAMEL_OR_SNAKE_CASE_TO_WORDS = r"^[a-z\d_\-]+|[A-Z\d_\-][^A-Z\d_\-]*"

class ArticlesRepository(BaseRepository):  # noqa: WPS214
    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)
        self._profiles_repo = ProfilesRepository(conn)

    async def create_article(  # noqa: WPS211
        self,
        *,
        slug: str,
        title: str,
        description: str,
        image: str,
        body: str,
        author: User,
        tags: Optional[Sequence[str]] = None,
    ) -> Article:
        async with self.connection.transaction():
            article_row = await queries.create_new_article(
                self.connection,
                slug=slug,
                title=title,
                description=description,
                image=image,
                body=body,
                author_username=author.username,
            )

            if tags:
                await self._tags_repo.create_tags_that_dont_exist(tags=tags)
                await self._link_article_with_tags(slug=slug, tags=tags)

        return await self._get_article_from_db_record(
            article_row=article_row,
            slug=slug,
            author_username=article_row[AUTHOR_USERNAME_ALIAS],
            requested_user=author,
        )

    async def update_article(  # noqa: WPS211
        self,
        *,
        article: Article,
        slug: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        image: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Article:
        updated_article = article.copy(deep=True)
        updated_article.slug = slug or updated_article.slug
        updated_article.title = title or article.title
        updated_article.body = body or article.body
        updated_article.image = image or article.image
        updated_article.description = description or article.description

        async with self.connection.transaction():
            updated_article.updated_at = await queries.update_article(
                self.connection,
                slug=article.slug,
                author_username=article.author.username,
                new_slug=updated_article.slug,
                new_title=updated_article.title,
                new_body=updated_article.body,
                new_image=updated_article.image,
                new_description=updated_article.description,
            )

        return updated_article
    
    async def get_articles_for_feed(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        requested_user: User,
    ) -> List[Article]:
        articles_rows = await queries.get_articles_for_feed(
            self.connection,
            limit=limit,
            offset=offset,
        )
        return [
            await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=requested_user,
            )
            for article_row in articles_rows
        ]

    async def filter_articles(  # noqa: WPS211
        self,
        *,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        favorited: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        requested_user: Optional[User] = None,
    ) -> List[Article]:
        query_params: List[Union[str, int]] = []
        query_params_count = 0

        # fmt: off
        query = Query.from_(
            articles,
        ).select(
            articles.id,
            articles.slug,
            articles.title,
            articles.description,
            articles.body,
            articles.created_at,
            articles.updated_at,
            Query.from_(
                users,
            ).where(
                users.id == articles.author_id,
            ).select(
                users.username,
            ).as_(
                AUTHOR_USERNAME_ALIAS,
            ),
        )
        # fmt: on

        if tag:
            query_params.append(tag)
            query_params_count += 1

            # fmt: off
            query = query.join(
                articles_to_tags,
            ).on(
                (articles.id == articles_to_tags.article_id) & (
                    articles_to_tags.tag == Query.from_(
                        tags_table,
                    ).where(
                        tags_table.tag == Parameter(query_params_count),
                    ).select(
                        tags_table.tag,
                    )
                ),
            )
            # fmt: on

        if author:
            query_params.append(author)
            query_params_count += 1

            # fmt: off
            query = query.join(
                users,
            ).on(
                (articles.author_id == users.id) & (
                    users.id == Query.from_(
                        users,
                    ).where(
                        users.username == Parameter(query_params_count),
                    ).select(
                        users.id,
                    )
                ),
            )
            # fmt: on

        if favorited:
            query_params.append(favorited)
            query_params_count += 1

            # fmt: off
            query = query.join(
                favorites,
            ).on(
                (articles.id == favorites.article_id) & (
                    favorites.user_id == Query.from_(
                        users,
                    ).where(
                        users.username == Parameter(query_params_count),
                    ).select(
                        users.id,
                    )
                ),
            )
            # fmt: on

        query = query.limit(Parameter(query_params_count + 1)).offset(
            Parameter(query_params_count + 2),
        )
        query_params.extend([limit, offset])

        articles_rows = await self.connection.fetch(query.get_sql(), *query_params)

        return [
            await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=requested_user,
            )
            for article_row in articles_rows
        ]

    async def _get_article_from_db_record(
        self,
        *,
        article_row: Record,
        slug: str,
        author_username: str,
        requested_user: Optional[User],
    ) -> Article:
        return Article(
            id_=article_row["id"],
            slug=slug,
            title=article_row["title"],
            description=article_row["description"],
            body=article_row["body"],
            image="",
            tags=[],
            author=await self._profiles_repo.get_profile_by_username(
                username=author_username,
                requested_user=requested_user,
            ),
            favorited=False,
            favorites_count=0
            if requested_user
            else False,
            created_at=article_row["created_at"],
            updated_at=article_row["updated_at"],
        )
    
    async def get_article_by_slug(
        self,
        *,
        slug: str,
        requested_user: Optional[User] = None,
    ) -> Article:
        article_row = await queries.get_article_by_slug(self.connection, slug=slug)
        if article_row:
            return await self._get_article_from_db_record(
                article_row=article_row,
                slug=article_row[SLUG_ALIAS],
                author_username=article_row[AUTHOR_USERNAME_ALIAS],
                requested_user=requested_user,
            )

        raise EntityDoesNotExist("article with slug {0} does not exist".format(slug))
    
async def check_article_exists(articles_repo: ArticlesRepository, slug: str) -> bool:
    try:
        await articles_repo.get_article_by_slug(slug=slug)
    except EntityDoesNotExist:
        return False

    return True

def get_slug_for_article(title: str) -> str:
    return slugify(title)

def check_user_can_modify_article(article: Article, user: User) -> bool :
    return article.author.username == user.username