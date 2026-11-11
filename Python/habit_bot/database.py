import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Date, ForeignKey, select
from datetime import datetime, date

DB_URL = "sqlite+aiosqlite:///bot_database.sqlite3"

engine = create_async_engine(DB_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.telegram_id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[str | None] = mapped_column(String(20), nullable=True)

class Habit(Base):
    __tablename__ = "habits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.telegram_id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    target_value: Mapped[int] = mapped_column(Integer, default=1) # e.g., 2 Liters or 1 times

class HabitLog(Base):
    __tablename__ = "habit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"))
    telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    log_date: Mapped[str] = mapped_column(String(20)) # YYYY-MM-DD
    current_progress: Mapped[int] = mapped_column(Integer, default=0)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)