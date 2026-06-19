import httpx
from app.core.config import settings

class GitHubService:
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"
        
    async def get_pr_diff(self, repo_name: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{repo_name}/pulls/{pr_number}"
        
        # We need the diff explicitly
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
            
    async def post_review_comment(self, repo_name: str, pr_number: int, commit_id: str, body: str, path: str, line: int):
        url = f"{self.base_url}/repos/{repo_name}/pulls/{pr_number}/comments"
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "side": "RIGHT"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

github_service = GitHubService()
