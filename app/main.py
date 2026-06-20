from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1.webhooks import github
from app.api.v1 import reviews

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(github.router, prefix=f"{settings.API_V1_STR}/webhooks/github", tags=["webhooks"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["analytics"])


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
