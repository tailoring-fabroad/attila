from typing import Optional, Union
from asyncpg import Connection

from app.repositories.queries.queries import queries
from app.repositories.data.base import BaseRepository
from app.repositories.data.authentication import AuthenticationRepository
from app.models.domain.profiles import Profile
from app.models.domain.users import User

UserLike = Union[User, Profile]

class ProfilesRepository(BaseRepository):
    def __init__(self, conn: Connection):
        super().__init__(conn)
        self._authentication_repository = AuthenticationRepository(conn)

    async def get_profile_by_username(
        self,
        *,
        username: str,
        requested_user: Optional[UserLike],
    ) -> Profile:
        user = await self._authentication_repository.get_user_by_username(username=username)

        profile = Profile(username=user.username, bio=user.bio, image=user.image)
        if requested_user:
            profile.following = await self.is_user_following_for_another_user(
                target_user=user,
                requested_user=requested_user,
            )

        return profile
    
    async def is_user_following_for_another_user(
        self,
        *,
        target_user: UserLike,
        requested_user: UserLike,
    ) -> bool:
        return (
            await queries.is_user_following_for_another(
                self.connection,
                follower_username=requested_user.username,
                following_username=target_user.username,
            )
        )["is_following"]