import pytest
from httpx import AsyncClient
from app.main import app
from app.db.session import get_db
from app.db.models import ReviewLog

pytestmark = pytest.mark.asyncio

class MockResult:
    def __init__(self, items):
        self._items = items
    def scalars(self):
        class MockScalars:
            def all(self_inner):
                return self._items
        return MockScalars()

class MockAsyncSession:
    def __init__(self, data):
        self.data = data
    async def execute(self, query):
        return MockResult(self.data)

async def test_get_recent_reviews(async_client: AsyncClient):
    fake_reviews = [
        ReviewLog(id=1, repo_name="Nik118/test_repo", pr_number=1, status="completed")
    ]
    
    async def override_get_db():
        yield MockAsyncSession(fake_reviews)
        
    app.dependency_overrides[get_db] = override_get_db
    
    response = await async_client.get("/api/v1/reviews/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["repo_name"] == "Nik118/test_repo"
    assert data[0]["status"] == "completed"
    
    app.dependency_overrides.clear()

async def test_get_repo_reviews_not_found(async_client: AsyncClient):
    async def override_get_db():
        yield MockAsyncSession([]) # Return empty list
        
    app.dependency_overrides[get_db] = override_get_db
    
    response = await async_client.get("/api/v1/reviews/Nik118/missing_repo")
    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this repository."
    
    app.dependency_overrides.clear()
