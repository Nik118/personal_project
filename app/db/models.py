from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, Text

class Base(DeclarativeBase):
    pass

class ReviewLog(Base):
    __tablename__ = "review_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repo_name: Mapped[str] = mapped_column(String, index=True)
    pr_number: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String, default="pending") # e.g., 'pending', 'completed', 'failed'
    comments_posted: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
