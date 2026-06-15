# Job Radar AI - Email Job Matcher & Parser

Job Radar AI is an intelligent pipeline that connects to your Gmail inbox, retrieves unread job notification emails, evaluates them against your specific profile requirements using the Google Gemini API, and displays matching results on a responsive local dashboard.

---

## Features

- **Gmail IMAP Fetching**: Securely logs in and uses `X-GM-RAW` syntax to search unread job notification emails (from LinkedIn, Indeed, etc.).
- **LLM Job Evaluation**: Supports two providers:
  - **Google Gemini**: Uses `gemini-2.5-flash` with a structured `TypedDict` response schema.
  - **Ollama (Local)**: Runs completely offline using local models like `gemma4:latest` with JSON format enforcement.
- **SQLite Database Tracking**: Stores evaluated jobs and records processed emails to avoid duplicate parsing.
- **Interactive Dashboard**: Serves a local web interface to review jobs, filter by match score, and track application status (`new`, `applied`, `rejected`).
- **Dashboard HTTP API**: Updates the application state dynamically from the web page.

---

## Project Structure

```text
├── main.py              # Main execution entrypoint (pipeline, dry-run, and server)
├── config.json          # Target profile configuration (roles, experience, locations)
├── requirements.txt     # Python package dependencies
├── dashboard.html       # Dynamic HTML page generated for the matches dashboard
├── src/
│   ├── db.py            # SQLite database schema and operations
│   ├── imap_client.py   # Gmail IMAP fetching client
│   ├── evaluator.py     # Gemini API structured-output job evaluator
│   ├── parser.py        # Helper to clean and strip email HTML bodies
│   └── generator.py     # Jinja2-based dashboard generator
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.9+
- A Google Account with [App Passwords](https://support.google.com/accounts/answer/185833) enabled for Gmail IMAP.
- A Google Gemini API Key from [Google AI Studio](https://ai.studio).

### 2. Install Dependencies
Clone the repository and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory by copying the sample:
```bash
cp .env.sample .env
```
Open `.env` and fill in your credentials. You can select either Google Gemini or Ollama as your evaluation provider:

```ini
IMAP_SERVER=imap.gmail.com
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# Choose provider: 'gemini' (requires API key) or 'ollama' (requires local server)
LLM_PROVIDER=ollama

# Google Gemini Config
GEMINI_API_KEY=your_gemini_api_key

# Ollama Config
OLLAMA_MODEL=gemma4:latest
OLLAMA_URL=http://localhost:11434
```

### 4. Target Preferences
Modify `config.json` in the root folder to customize your matching preferences:
```json
{
  "target_roles": ["Director of Product Management", "Group Product Manager", "Principal Product Manager"],
  "target_locations": ["Bengaluru", "Bangalore", "Remote"],
  "min_experience_years": 10,
  "required_experience": "10+ years of product management experience",
  "min_relevance_score": 6
}
```

---

## How to Run

### Run the Pipeline
Fetch unread emails, evaluate them, store them in the database, and regenerate the dashboard:
```bash
python main.py
```

### View the Dashboard
Launch the local HTTP server to view your matches and update application statuses:
```bash
python main.py --serve
```
The dashboard will open automatically in your browser at `http://127.0.0.1:8000/`.

### Run a Simulation (Dry-Run)
Test the evaluation and dashboard creation without connecting to a live Gmail server using a mock job email:
```bash
python main.py --dry-run
```
