import json
import urllib.request
import urllib.error
from backend.config import settings
from backend.api.schemas import AnalysisResult
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def generate_suggestions(result: AnalysisResult) -> str:
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        logger.warning("OpenAI API key not set. Skipping AI suggestions.")
        return "AI suggestions are disabled. Please provide an OPENAI_API_KEY."

    try:
        dead_code_items = result.dead_code[:50]
        unused_imports_items = result.unused_imports[:50]
        unused_dependencies_items = result.unused_dependencies[:30]
        
        dead_code_str = "\n".join([f"- {item.function_name} in {item.file_path}:{item.line_number}" for item in dead_code_items])
        if len(result.dead_code) > 50:
            dead_code_str += f"\n- ... and {len(result.dead_code) - 50} more items."
            
        unused_imports_str = "\n".join([f"- {item.import_name} in {item.file_path}:{item.line_number}" for item in unused_imports_items])
        if len(result.unused_imports) > 50:
            unused_imports_str += f"\n- ... and {len(result.unused_imports) - 50} more items."
            
        unused_deps_str = ", ".join(unused_dependencies_items)
        if len(result.unused_dependencies) > 30:
            unused_deps_str += f", and {len(result.unused_dependencies) - 30} more dependencies."

        prompt = f"""
        You are an expert software engineer and code reviewer. Analyze the following repository issues and provide a brief, structured suggestion on how to address them safely.
        
        Repo: {result.repo_url}
        
        Dead Code (Unused Functions):
        {dead_code_str}
        
        Unused Imports:
        {unused_imports_str}
        
        Unused Dependencies:
        {unused_deps_str}
        
        Provide a concise, markdown-formatted guide detailing:
        1. Why these are risky (e.g. bloat, security).
        2. Safe steps to remove them (e.g. double checking dynamic imports, running tests).
        """
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=json.dumps({
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5,
                        "max_tokens": 4096
                    }).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )
                
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    logger.warning(f"Rate limited (429). Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    logger.error(f"Error communicating with OpenAI API: {e} - {e.read()}")
                    break  # Break to fallback
            except urllib.error.URLError as e:
                logger.error(f"Error communicating with OpenAI API: {e}")
                break  # Break to fallback
                
        # --- FALLBACK SUGGESTIONS ---
        logger.info("Using fallback suggestions because AI API failed or quota was exceeded.")
        fallback = f"### ⚠️ AI Quota Exceeded - Fallback Suggestions\n\nWe couldn't reach the AI for personalized advice, but based on your repository analysis, here are the recommended steps:\n\n"
        
        if result.dead_code:
            fallback += f"#### 🧟‍♂️ Dead Code ({len(result.dead_code)} issues found)\n"
            fallback += "- **Risk**: Dead code inflates your codebase size, makes navigation harder, and can confuse developers.\n"
            fallback += "- **Action**: Safely remove these unused functions. Before deleting, ensure they aren't called dynamically (e.g., via reflection or `getattr`). Run your unit tests after removal.\n\n"
            
        if result.unused_imports:
            fallback += f"#### 🧹 Unused Imports ({len(result.unused_imports)} issues found)\n"
            fallback += "- **Risk**: Unused imports slow down execution, increase memory usage, and can cause confusing naming conflicts.\n"
            fallback += "- **Action**: Use an automated tool like `autoflake`, `isort`, or `ruff` to safely remove unused imports across your project.\n\n"
            
        if result.unused_dependencies:
            fallback += f"#### 📦 Unused Dependencies ({len(result.unused_dependencies)} issues found)\n"
            fallback += "- **Risk**: Unnecessary packages increase bundle size, slow down CI/CD pipelines, and introduce potential security vulnerabilities from third-party code.\n"
            fallback += "- **Action**: Run `pip uninstall <package>` for each unused item. Also remove them from your `requirements.txt` or `pyproject.toml`.\n\n"
            
        if not result.dead_code and not result.unused_imports and not result.unused_dependencies:
            fallback += "**Great job!** No major issues were found in your codebase.\n"
            
        return fallback

    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return f"Failed to generate AI suggestions due to an error: {str(e)}"

