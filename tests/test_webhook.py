import pytest
from httpx import AsyncClient, ASGITransport
import hmac
import hashlib
from app.main import app
from app.core.config import settings
import json

@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"{settings.API_V1_STR}/webhooks/github/",
            json={"action": "opened"},
            headers={"X-Hub-Signature-256": "invalid_sig", "X-GitHub-Event": "pull_request"}
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid signature"}

@pytest.mark.asyncio
async def test_webhook_valid_signature_no_celery(mocker):
    # Mock celery task to not actually run
    mocker.patch("app.worker.tasks.process_pr_review.delay")
    
    payload_dict = {
        "action": "opened",
        "pull_request": {"number": 1, "head": {"sha": "abc"}},
        "repository": {"full_name": "user/repo"}
    }
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    
    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    )
    signature = "sha256=" + hash_object.hexdigest()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"{settings.API_V1_STR}/webhooks/github/",
            content=payload_bytes,
            headers={
                "X-Hub-Signature-256": signature, 
                "X-GitHub-Event": "pull_request", 
                "Content-Type": "application/json"
            }
        )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Review task queued for user/repo PR #1"}
