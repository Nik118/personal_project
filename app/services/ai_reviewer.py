from google import genai
from google.genai import types
from app.core.config import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class AIReviewerService:
    
    async def analyze_diff(self, diff_text: str) -> list[dict]:
        """
        Analyzes the PR diff and returns a list of actionable comments.
        We ask the model to return JSON to make it parsable.
        """
        prompt = f"""
        You are an expert Senior Staff Software Engineer. 
        Review the following code diff and provide constructive, actionable feedback.
        Only comment on significant issues: bugs, security vulnerabilities, performance issues, or major style violations.
        
        Return the response strictly as a JSON list of objects. Each object should have:
        - "file_path": The path of the file being modified.
        - "line_number": The specific line number in the NEW code where the comment applies.
        - "comment": The review comment itself.
        
        If there are no significant issues, return an empty list [].
        
        Code Diff:
        {diff_text}
        """
        
        try:
            response = await client.aio.models.generate_content(
                model="gemini-1.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            reviews = json.loads(response.text)
            if not isinstance(reviews, list):
                print("Warning: AI returned JSON, but it was not a list.")
                return []
            return reviews
        except json.JSONDecodeError as e:
            print(f"Failed to decode AI JSON response: {e}")
            return []
        except Exception as e:
            print(f"Failed to parse AI response: {e}")
            return []

ai_reviewer = AIReviewerService()
