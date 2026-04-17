<<<<<<< HEAD
# repo-doctor-ai
=======
# RepoDoctor AI

A FastAPI backend for analyzing GitHub repositories to find:
- Dead code (defined but uncalled functions)
- Unused imports
- Unused dependencies
- Code suggestions via AI (using Groq API)

## Setup

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables. Add your access key to `.env`:
```
GROQ_API_KEY="your_groq_api_key_here"
```

## Running the application

```bash
uvicorn backend.main:app --reload
```

## Endpoints

- `POST /analyze`: Request tracking for analysis.
    ```json
    { "repo_url": "https://github.com/user/repo" }
    ```
- `GET /report/{id}`: Retrieves the Markdown report.
>>>>>>> fd5c90b (add gitignore and remove env)
