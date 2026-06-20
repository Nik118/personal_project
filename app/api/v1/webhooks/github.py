import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from app.worker.tasks import process_pr_review

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def verify_signature(payload_body: bytes, signature_header: str | None) -> bool:
    if not signature_header:
        return False
        
    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/")
@limiter.limit("5/minute")
async def handle_github_webhook(request: Request):
    # Verify the payload signature
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()
    
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event")
    
    # We only care about pull request events
    if event_type == "pull_request":
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
            
        action = payload.get("action")
        
        # Trigger review on open or synchronize (new commits)
        if action in ["opened", "synchronize"]:
            pr_number = payload["pull_request"]["number"]
            repo_name = payload["repository"]["full_name"]
            commit_id = payload["pull_request"]["head"]["sha"]
            
            # Enqueue the Celery task for async processing
            process_pr_review.delay(repo_name, pr_number, commit_id)
            
            return {"message": f"Review task queued for {repo_name} PR #{pr_number}"}
            
    return {"message": "Event ignored"}
