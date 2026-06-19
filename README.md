# AI-Powered Code Review Assistant

This project is an advanced, scalable backend application that acts as an automated AI code review assistant. It listens for GitHub Pull Request webhooks, asynchronously fetches the code diffs, analyzes them using an LLM (Google Gemini API), and posts actionable review comments back to the PR.

Built with performance, concurrency, and security in mind, this project demonstrates robust system architecture using FastAPI, Celery, Redis, and PostgreSQL.

## Architecture Highlights

- **Asynchronous Webhooks**: Built with **FastAPI**, ensuring rapid response times to GitHub webhooks without timeouts.
- **Background Task Processing**: Utilizes **Celery** with a **Redis** broker to handle potentially slow 3rd-party API calls (GitHub API, LLM API) in the background.
- **Security**: Validates incoming GitHub webhooks using HMAC SHA-256 signatures to prevent unauthorized requests.
- **AI Integration**: Leverages `google-generativeai` (Gemini 1.5 Pro) to provide context-aware, senior-level code reviews.
- **Database Ready**: Integrates **SQLAlchemy (Asyncpg)** for PostgreSQL, laying the foundation for tracking review logs and repository configurations.

## System Workflow

1. A developer opens or synchronizes a Pull Request on a GitHub repository.
2. GitHub sends a webhook payload to the FastAPI `/api/v1/webhooks/github/` endpoint.
3. The API validates the HMAC signature. If valid, it enqueues a Celery task and responds with `200 OK` immediately.
4. The Celery worker picks up the task, authenticates with GitHub, and fetches the raw code diff.
5. The worker sends the diff to the Gemini API with a strict system prompt.
6. The Gemini API returns structured JSON containing review comments linked to specific file paths and line numbers.
7. The worker uses the GitHub API to post these comments directly onto the Pull Request.

## Prerequisites

- Python 3.10+
- [Redis](https://redis.io/docs/getting-started/) (Running on `localhost:6379`)
- [PostgreSQL](https://www.postgresql.org/download/) (Database named `code_reviewer`)
- A [GitHub Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- A [Google Gemini API Key](https://ai.google.dev/)

## Installation & Setup

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   GITHUB_WEBHOOK_SECRET=your_custom_secret_string
   GITHUB_TOKEN=your_github_personal_access_token
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/code_reviewer
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

3. **Run the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   *The server will run on `http://127.0.0.1:8000`.*

4. **Run the Celery Worker:**
   Open a new terminal window and start the background worker:
   ```bash
   celery -A app.worker.celery_app worker --loglevel=info
   ```

## Webhook Configuration (Local Testing)

To receive webhooks locally, expose your server using [ngrok](https://ngrok.com/):
```bash
ngrok http 8000
```

**In your GitHub Repository:**
1. Navigate to **Settings** -> **Webhooks** -> **Add webhook**.
2. **Payload URL**: `https://<your-ngrok-url>/api/v1/webhooks/github/`
3. **Content type**: `application/json`
4. **Secret**: Enter your `GITHUB_WEBHOOK_SECRET`.
5. **Events**: Select "Let me select individual events" -> Check **Pull requests**.
6. Save the webhook.

## Running Tests
Run the pytest suite to ensure webhook signature validation works correctly:
```bash
pytest
```