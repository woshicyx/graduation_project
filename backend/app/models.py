from __future__ import annotations

from datetime import date
from typing import List

from sqlalchemy import BigInteger, Date, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    director: Mapped[str] = mapped_column(String(255), index=True)
    genres: Mapped[List[str]] = mapped_column(ARRAY(String))
    rating: Mapped[float] = mapped_column(Float)
    box_office: Mapped[int] = mapped_column(BigInteger)
    release_date: Mapped[date] = mapped_column(Date, index=True)
    poster_url: Mapped[str] = mapped_column(String(512))
    popularity: Mapped[float] = mapped_column(Float, index=True)
    synopsis: Mapped[str] = mapped_column(String)

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    movie_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), index=True
    )
    author: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)

    movie: Mapped[Movie] = relationship(back_populates="reviews")

