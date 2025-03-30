"""Typings for queries generated by aiosql"""

from typing import Optional

from asyncpg import Connection, Record

class UsersQueriesMixin:
    async def get_user_by_email(self, conn: Connection, *, email: str) -> Record: ...
    async def get_user_by_username(
        self, conn: Connection, *, username: str
    ) -> Record: ...
    async def create_new_user(
        self,
        conn: Connection,
        *,
        username: str,
        email: str,
        salt: str,
        hashed_password: str
    ) -> Record: ...
    async def update_user_by_username(
        self,
        conn: Connection,
        *,
        username: str,
        new_username: str,
        new_email: str,
        new_salt: str,
        new_password: str,
        new_bio: Optional[str],
        new_image: Optional[str]
    ) -> Record: ...

class Queries(
    UsersQueriesMixin,
): ...

queries: Queries