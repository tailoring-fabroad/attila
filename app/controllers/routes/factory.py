from fastapi import APIRouter

from app.controllers.routes import authentication, users, articles_common, articles_resource, media_common, media_resource, reviews, profiles, tags

router = APIRouter()
router.include_router(authentication.router, tags=["authentication"], prefix="/authentication")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(profiles.router, tags=["profiles"], prefix="/profiles")
router.include_router(articles_common.router, tags=["articles"], prefix="/articles")
router.include_router(articles_resource.router, tags=["articles"], prefix="/articles")
router.include_router(media_common.router, tags=["media"], prefix="/media")
router.include_router(media_resource.router, tags=["media"], prefix="/media")
router.include_router(reviews.router, tags=["reviews"], prefix="/articles/{slug}/reviews")
router.include_router(tags.router, tags=["tags"], prefix="/tags")
