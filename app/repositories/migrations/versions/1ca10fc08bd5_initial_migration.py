"""initial migration

Revision ID: 1ca10fc08bd5
Revises: 
Create Date: 2025-04-12 20:41:49.180681

"""
from typing import Tuple

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
import sqlalchemy.dialects.postgresql as pg

revision = '1ca10fc08bd5'
down_revision = None
branch_labels = None
depends_on = None

def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.current_timestamp()),
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
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_followers_to_followings_table() -> None:
    op.create_table(
        "followers_to_followings",
        sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("following_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_followers_to_followings", "followers_to_followings", ["follower_id", "following_id"])

def create_media_table() -> None:

    op.create_table(
        'media',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column('type', sa.Enum('image', 'video', 'audio', name='media_type', create_type=False), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('description', sa.Text),
        sa.Column('file_path', sa.Text, nullable=False),
        sa.Column('file_size', sa.BigInteger),
        sa.Column('mime_type', sa.String(50)),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_media_modtime
        BEFORE UPDATE ON media
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_media_images_table() -> None:

    op.create_table(
        'media_images',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('media_id', pg.UUID(as_uuid=True), sa.ForeignKey('media.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('width', sa.Integer),
        sa.Column('height', sa.Integer),
        sa.Column('format', sa.Enum('jpg', 'eps', name='image_format', create_type=False), nullable=False),
    )

def create_media_videos_table() -> None:

    op.create_table(
        'media_videos',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('media_id', pg.UUID(as_uuid=True), sa.ForeignKey('media.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('resolution', sa.String(50)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('format', sa.Enum('mp4', 'mov', name='video_format', create_type=False), nullable=False),
    )

def create_media_audios_table() -> None:
    op.create_table(
        'media_audios',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('media_id', pg.UUID(as_uuid=True), sa.ForeignKey('media.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('bitrate_kbps', sa.Integer),
        sa.Column('format', sa.String(20)),
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
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_article_modtime
        BEFORE UPDATE ON articles
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_tags_table() -> None:
    op.create_table("tags", sa.Column("tag", sa.Text, primary_key=True))

def create_articles_to_tags_table() -> None:
    op.create_table(
        "articles_to_tags",
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.Text, sa.ForeignKey("tags.tag", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_articles_to_tags", "articles_to_tags", ["article_id", "tag"])

def create_media_to_tags_table() -> None:
    op.create_table(
        "media_to_tags",
        sa.Column("media_id", pg.UUID(as_uuid=True), sa.ForeignKey("media.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.Text, sa.ForeignKey("tags.tag", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_media_to_tags", "media_to_tags", ["media_id", "tag"])

def create_favorite_articles_table() -> None:
    op.create_table(
        "favorite_articles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_favorite_articles", "favorite_articles", ["user_id", "article_id"])

def create_favorite_media_table() -> None:
    op.create_table(
        "favorite_medias",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", pg.UUID(as_uuid=True), sa.ForeignKey("media.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_favorite_medias", "favorite_medias", ["user_id", "media_id"])

def create_favorites_table() -> None:
    op.create_table(
        "favorite_articles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_primary_key("pk_favorites", "favorites", ["user_id", "article_id"])

def create_reviews_table() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_id", sa.Integer, sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_comment_modtime
        BEFORE UPDATE ON reviews
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_followers_to_followings_table()
    create_media_table()
    create_media_images_table()
    create_media_videos_table()
    create_media_audios_table()
    create_articles_table()
    create_tags_table()
    create_articles_to_tags_table()
    create_media_to_tags_table()
    create_favorite_articles_table()
    create_favorite_media_table()
    create_reviews_table()

def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("favorite_medias")
    op.drop_table("favorite_articles")
    op.drop_table("media_to_tags")
    op.drop_table("articles_to_tags")
    op.drop_table("tags")
    op.drop_table("articles")
    op.drop_table("media_audios")
    op.drop_table("media_videos")
    op.drop_table("media_images")
    op.drop_table("media")
    op.drop_table("followers_to_followings")
    op.drop_table("users")

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column")
