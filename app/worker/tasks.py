from asgiref.sync import async_to_sync
from app.worker.celery_app import celery_app
from app.services.github import github_service
from app.services.ai_reviewer import ai_reviewer
from app.db.session import AsyncSessionLocal
from app.db.models import ReviewLog
import logging

logger = logging.getLogger(__name__)

async def _process_review(repo_name: str, pr_number: int, commit_id: str, task_id: str):
    logger.info(f"Starting review for {repo_name} PR #{pr_number}")
    
    # Initialize DB log
    async with AsyncSessionLocal() as session:
        log = ReviewLog(repo_name=repo_name, pr_number=pr_number, status="pending")
        session.add(log)
        await session.commit()
        await session.refresh(log)
        log_id = log.id

    try:
        # 1. Fetch diff
        diff_text = await github_service.get_pr_diff(repo_name, pr_number)
        if not diff_text:
            logger.info("No diff found or diff is empty.")
            async with AsyncSessionLocal() as session:
                log = await session.get(ReviewLog, log_id)
                log.status = "completed"
                await session.commit()
            return
            
        # 2. Analyze diff
        reviews = await ai_reviewer.analyze_diff(diff_text)
        logger.info(f"AI generated {len(reviews)} comments.")
        
        # 3. Post comments
        comments_posted = 0
        for review in reviews:
            path = review.get("file_path")
            line = review.get("line_number")
            body = review.get("comment", "Review comment.")
            
            if path is not None and line is not None:
                await github_service.post_review_comment(
                    repo_name=repo_name,
                    pr_number=pr_number,
                    commit_id=commit_id,
                    body=str(body),
                    path=str(path),
                    line=int(line)
                )
                comments_posted += 1
            else:
                logger.warning(f"Skipping comment due to missing path or line: {review}")
        
        # Update DB on success
        async with AsyncSessionLocal() as session:
            log = await session.get(ReviewLog, log_id)
            log.status = "completed"
            log.comments_posted = comments_posted
            await session.commit()

    except Exception as e:
        logger.error(f"Failed to process review: {e}")
        # Update DB on failure
        async with AsyncSessionLocal() as session:
            log = await session.get(ReviewLog, log_id)
            log.status = "failed"
            log.error_message = str(e)
            await session.commit()
        raise e  # Reraise to trigger Celery retry

@celery_app.task(bind=True, name="app.worker.tasks.process_pr_review", max_retries=3, default_retry_delay=60)
def process_pr_review(self, repo_name: str, pr_number: int, commit_id: str):
    """
    Celery task wrapper to run the async review process.
    Retries up to 3 times on failure with a 60-second delay.
    """
    try:
        async_to_sync(_process_review)(repo_name, pr_number, commit_id, self.request.id)
    except Exception as exc:
        raise self.retry(exc=exc)
