import google.generativeai as genai
import os
import json
import typing
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# Define the TypedDict schema for structured Gemini outputs
class JobEvaluation(typing.TypedDict):
    job_title: str
    company: str
    location: str
    job_type: str  # Remote, Hybrid, Onsite, or Unknown
    experience_required: str
    relevance_score: int  # 0 to 10
    explanation: str
    skills: list[str]
    salary: str

class JobEvaluator:
    def __init__(self, config_path="config.json"):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.provider == "gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                print("WARNING: GEMINI_API_KEY not set in environment. Gemini evaluation will not work.")
        
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:latest")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip('/')
        self.config = self._load_config(config_path)

    def _load_config(self, config_path):
        if not os.path.exists(config_path):
            return {
                "target_roles": ["Director of Product Management", "Group Product Manager", "Principal Product Manager"],
                "target_locations": ["Bengaluru", "Bangalore", "Remote"],
                "min_experience_years": 10,
                "required_experience": "10+ years of product management experience",
                "min_relevance_score": 6
            }
        with open(config_path, "r") as f:
            return json.load(f)

    def evaluate_email(self, email_subject, email_sender, email_body):
        """
        Sends the email content to the selected provider (Gemini or Ollama) for job evaluation.
        """
        if self.provider == "gemini":
            return self._evaluate_with_gemini(email_subject, email_sender, email_body)
        elif self.provider == "ollama":
            return self._evaluate_with_ollama(email_subject, email_sender, email_body)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _evaluate_with_gemini(self, email_subject, email_sender, email_body):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")

        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = self._build_prompt(email_subject, email_sender, email_body)
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=JobEvaluation,
                    temperature=0.1,  # Low temperature for factual parsing
                )
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._get_fallback_evaluation(str(e))

    def _evaluate_with_ollama(self, email_subject, email_sender, email_body):
        prompt = self._build_prompt(email_subject, email_sender, email_body)
        
        # System instructions to enforce JSON output format
        system_instructions = (
            "You are a structured parser. You MUST respond ONLY with a valid JSON object matching the requested schema. "
            "Do not include any markdown formatting, backticks (like ```json), or explanation text before or after the JSON.\n"
            "SCHEMA:\n"
            "{\n"
            "  \"job_title\": string,\n"
            "  \"company\": string,\n"
            "  \"location\": string,\n"
            "  \"job_type\": string (Remote, Hybrid, Onsite, or Unknown),\n"
            "  \"experience_required\": string,\n"
            "  \"relevance_score\": integer (0 to 10),\n"
            "  \"explanation\": string,\n"
            "  \"skills\": array of strings,\n"
            "  \"salary\": string\n"
            "}"
        )
        
        url = f"{self.ollama_url}/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=60) as response:
                resp_data = response.read().decode("utf-8")
                resp_json = json.loads(resp_data)
                
                content = resp_json.get("message", {}).get("content", "").strip()
                result = json.loads(content)
                
                return self._sanitize_evaluation_result(result)
                
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return self._get_fallback_evaluation(str(e))

    def _build_prompt(self, email_subject, email_sender, email_body):
        return f"""
You are an expert technical recruitment advisor. Analyze the following email content and evaluate the job opportunity against the user's target profile.

USER PROFILE PREFERENCES:
- Target Roles: {", ".join(self.config.get('target_roles', []))}
- Target Locations: {", ".join(self.config.get('target_locations', []))}
- Required Experience: {self.config.get('required_experience', '10+ years')} (Minimum {self.config.get('min_experience_years', 10)} years)
- Minimum Relevance Score Threshold: {self.config.get('min_relevance_score', 6)}/10

EMAIL CONTENT:
---
Subject: {email_subject}
Sender: {email_sender}

Body:
{email_body}
---

INSTRUCTIONS:
1. Determine if this email actually describes a job opening or job alert. If it is NOT a job description or job listing (e.g., it is a general newsletter, verification email, or unrelated chat), give it a relevance_score of 0 and set explanation to "Not a job email".
2. Evaluate how well this job matches the user's preferences.
3. Scoring Criteria (Relevance Score 0 to 10):
   - A score of 9-10 is a strong match: Role is a Director/Group/Principal PM, location is Bangalore/Bengaluru (or Remote), and requires 10+ years of experience.
   - A score of 7-8 is a moderate match: Role matches product management leadership, but perhaps location is hybrid/remote or experience is slightly lower (e.g. 8 years) or role is Senior PM with high scope.
   - A score of 5-6 is a low/mediocre match: Standard Product Manager role, or location is in India but not Bangalore, or experience is 5-7 years.
   - A score of 1-4 is a poor match: Unrelated role, incorrect location (e.g. US onsite), or entry level.
   - A score of 0 is for non-job emails.
4. Extract the job details exactly as requested by the JSON schema.
"""

    def _sanitize_evaluation_result(self, result):
        # Handle case where relevance_score is parsed as string or missing
        try:
            score = int(result.get("relevance_score", 0))
        except ValueError:
            score = 0
            
        sanitized = {
            "job_title": str(result.get("job_title", "Unknown")),
            "company": str(result.get("company", "Unknown")),
            "location": str(result.get("location", "Unknown")),
            "job_type": str(result.get("job_type", "Unknown")),
            "experience_required": str(result.get("experience_required", "Unknown")),
            "relevance_score": score,
            "explanation": str(result.get("explanation", "")),
            "skills": list(result.get("skills", [])),
            "salary": str(result.get("salary", "Unknown"))
        }
        return sanitized

    def _get_fallback_evaluation(self, error_msg):
        return {
            "job_title": "Failed to evaluate",
            "company": "Unknown",
            "location": "Unknown",
            "job_type": "Unknown",
            "experience_required": "Unknown",
            "relevance_score": 0,
            "explanation": f"Error: {error_msg}",
            "skills": [],
            "salary": "Unknown"
        }
