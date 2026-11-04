import os
from datetime import datetime
from typing import AsyncGenerator, Optional
from sqlalchemy import ForeignKey, Text, DateTime, String, URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/chhotu_db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

url = URL.create(
    drivername="postgresql",
    username=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    database=os.environ.get("POSTGRES_DB"),
    port=os.environ.get("POSTGRES_PORT"),
)


class Base(DeclarativeBase):
    pass

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    sender: Mapped[str] = mapped_column(String(20))  # "human" or "ai"
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session