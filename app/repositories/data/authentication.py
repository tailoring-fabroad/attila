from app.models.domain.authentication import Authentication
from app.repositories.errors import EntityDoesNotExist
from app.repositories.data.base import BaseRepository
from app.repositories.queries.queries import queries

class AuthenticationRepository(BaseRepository):
    async def get_user_by_email(self, *, email: str) -> Authentication:
        user_row = await queries.get_user_by_email(self.connection, email=email)
        if user_row:
            return Authentication(**user_row)
        raise EntityDoesNotExist("user with email {0} does not exist".format(email))

    async def get_user_by_username(self, *, username: str) -> Authentication:
        user_row = await queries.get_user_by_username(
            self.connection,
            username=username,
        )
        if user_row:
            return Authentication(**user_row)
        raise EntityDoesNotExist("user with username {0} does not exist".format(username))
    
    async def create_user(self, *, username: str,email: str, password: str) -> Authentication:
        user = Authentication(username=username, email=email)
        user.change_password(password)
        async with self.connection.transaction():
            user_row = await queries.create_new_user(
                self.connection,
                username=user.username,
                email=user.email,
                salt=user.salt,
                hashed_password=user.hashed_password,
            )
        return user.copy(update=dict(user_row))
    
async def check_username_is_taken(authentication_repository: AuthenticationRepository, username: str) -> bool:
    try:
        await authentication_repository.get_user_by_username(username=username)
        return True
    except EntityDoesNotExist:
        return False

async def check_email_is_taken(authentication_repository: AuthenticationRepository, email: str) -> bool:
    try:
        await authentication_repository.get_user_by_email(email=email)
        return True
    except EntityDoesNotExist:
        return False