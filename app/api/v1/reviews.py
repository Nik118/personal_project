from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import ReviewLog

router = APIRouter()

@router.get("/")
async def get_recent_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the most recent AI code reviews."""
    result = await db.execute(
        select(ReviewLog).order_by(desc(ReviewLog.created_at)).offset(skip).limit(limit)
    )
    reviews = result.scalars().all()
    return reviews

@router.get("/{repo_name:path}")
async def get_repo_reviews(
    repo_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Fetch recent AI code reviews for a specific repository."""
    result = await db.execute(
        select(ReviewLog)
        .where(ReviewLog.repo_name == repo_name)
        .order_by(desc(ReviewLog.created_at))
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this repository.")
    return reviews
