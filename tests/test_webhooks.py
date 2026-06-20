import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient
from app.core.config import settings

pytestmark = pytest.mark.asyncio

def generate_signature(payload: bytes) -> str:
    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    return "sha256=" + hash_object.hexdigest()

async def test_webhook_invalid_signature(async_client: AsyncClient, mock_celery_delay):
    payload = {"action": "opened"}
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=invalid_fake_signature"
    }
    
    response = await async_client.post("/api/v1/webhooks/github/", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
    mock_celery_delay.assert_not_called()

async def test_webhook_valid_signature_wrong_event(async_client: AsyncClient, mock_celery_delay):
    payload = {"action": "push"}
    payload_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": generate_signature(payload_bytes)
    }
    
    response = await async_client.post("/api/v1/webhooks/github/", content=payload_bytes, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Event ignored"}
    mock_celery_delay.assert_not_called()

async def test_webhook_valid_signature_pr_opened(async_client: AsyncClient, mock_celery_delay):
    payload = {
        "action": "opened",
        "repository": {"full_name": "Nik118/test_repo"},
        "pull_request": {
            "number": 42,
            "head": {"sha": "abcdef123456"}
        }
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": generate_signature(payload_bytes)
    }
    
    response = await async_client.post("/api/v1/webhooks/github/", content=payload_bytes, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Review task queued for Nik118/test_repo PR #42"}
    
    mock_celery_delay.assert_called_once_with("Nik118/test_repo", 42, "abcdef123456")
