from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.webhooks import github

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(github.router, prefix=f"{settings.API_V1_STR}/webhooks/github", tags=["webhooks"])


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
