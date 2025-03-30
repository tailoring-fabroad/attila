from fastapi import APIRouter

from app.controllers.routes import authentication, articles, reviews, profiles, tags, users

router = APIRouter()
router.include_router(authentication.router, tags=["authentication"], prefix="/authentication")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(profiles.router, tags=["profiles"], prefix="/profiles")
router.include_router(articles.router, tags=["articles"])
router.include_router(reviews.router, tags=["reviews"], prefix="/articles/{slug}/reviews")
router.include_router(tags.router, tags=["tags"], prefix="/tags")
