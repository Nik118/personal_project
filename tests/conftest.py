import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_celery_delay():
    with patch("app.api.v1.webhooks.github.process_pr_review.delay") as mock_delay:
        yield mock_delay
