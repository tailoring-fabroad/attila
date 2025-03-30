"""auto migration

Revision ID: 26dd7d466714
Revises: 
Create Date: 2025-03-30 15:44:05.087397

"""
from typing import Tuple

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

revision = '26dd7d466714'
down_revision = None
branch_labels = None
depends_on = None

def create_updated_at_trigger() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS
    $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    )

def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.current_timestamp(),
        ),
    )

def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("hashed_password", sa.Text),
        sa.Column("bio", sa.Text, nullable=False, server_default=""),
        sa.Column("image", sa.Text),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_followers_to_followings_table() -> None:
    op.create_table(
        "followers_to_followings",
        sa.Column(
            "follower_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "following_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_followers_to_followings",
        "followers_to_followings",
        ["follower_id", "following_id"],
    )

def create_articles_table() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("image", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")
        ),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_article_modtime
            BEFORE UPDATE
            ON articles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_tags_table() -> None:
    op.create_table("tags", sa.Column("tag", sa.Text, primary_key=True))

def create_articles_to_tags_table() -> None:
    op.create_table(
        "articles_to_tags",
        sa.Column(
            "article_id",
            sa.Integer,
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tag",
            sa.Text,
            sa.ForeignKey("tags.tag", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key(
        "pk_articles_to_tags", "articles_to_tags", ["article_id", "tag"]
    )

def create_favorites_table() -> None:
    op.create_table(
        "favorites",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "article_id",
            sa.Integer,
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_primary_key("pk_favorites", "favorites", ["user_id", "article_id"])

def create_reviews_table() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "author_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "article_id",
            sa.Integer,
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_comment_modtime
            BEFORE UPDATE
            ON reviews
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_followers_to_followings_table()
    create_articles_table()
    create_tags_table()
    create_articles_to_tags_table()
    create_favorites_table()
    create_reviews_table()

def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("favorites")
    op.drop_table("articles_to_tags")
    op.drop_table("tags")
    op.drop_table("articles")
    op.drop_table("followers_to_followings")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
