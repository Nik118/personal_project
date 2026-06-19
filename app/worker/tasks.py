from asgiref.sync import async_to_sync
from app.worker.celery_app import celery_app
from app.services.github import github_service
from app.services.ai_reviewer import ai_reviewer

async def _process_review(repo_name: str, pr_number: int, commit_id: str):
    print(f"Starting review for {repo_name} PR #{pr_number}")
    
    # 1. Fetch diff
    try:
        diff_text = await github_service.get_pr_diff(repo_name, pr_number)
    except Exception as e:
        print(f"Failed to fetch diff: {e}")
        return
        
    if not diff_text:
        print("No diff found or diff is empty.")
        return
        
    # 2. Analyze diff
    reviews = await ai_reviewer.analyze_diff(diff_text)
    print(f"AI generated {len(reviews)} comments.")
    
    # 3. Post comments
    for review in reviews:
        try:
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
            else:
                print(f"Skipping comment due to missing path or line: {review}")
        except Exception as e:
            print(f"Failed to post comment for {review.get('file_path')}:{review.get('line_number')} - {e}")

@celery_app.task(name="app.worker.tasks.process_pr_review")
def process_pr_review(repo_name: str, pr_number: int, commit_id: str):
    """
    Celery task wrapper to run the async review process.
    """
    async_to_sync(_process_review)(repo_name, pr_number, commit_id)
